#!/usr/bin/env python3

# obs-prune-attach.py
#
# Part of 'Obsidian Tag Tools': https://github.com/Jachimo/obstagtools
#
# Removes attachments from an Obsidian Vault's Attachments directory
# that are not linked by a document in the vault.
# By default, lists files to delete, but doesn't actually delete them.

import pathlib
import shutil
import sys
import os
import logging
import argparse
from typing import Optional, List

import obs_vault


def main():
    parser = argparse.ArgumentParser(description='Delete unused attachments in an Obsidian vault')
    parser.add_argument('vaultroot', help='Path to source vault (root directory of vault)')
    parser.add_argument('--attachmentpath', '-a', type=str, help='Path to attachments directory')
    parser.add_argument('--delete', '-d', action='store_true', help='Actually delete files (DANGER!)')
    parser.add_argument('--trash', '-t', type=str, help='Trash dir to move deletable files to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode (verbose output)')
    args = parser.parse_args()

    # Logging
    rootlogger = logging.getLogger()
    log_format: str = "[%(filename)20s,%(lineno)3s:%(funcName)20s] %(message)s"
    logging.basicConfig(format=log_format)
    logger = logging.getLogger(__name__)
    if args.debug:
        rootlogger.setLevel(logging.DEBUG)
        logger.debug('Debug output enabled')
    else:
        rootlogger.setLevel(logging.INFO)

    # Fail fast on invalid inputs
    if not isinstance(args.vaultroot, str):
        raise TypeError(f'Vault directory {args.vaultroot} is not a string')
    if args.trash:
        if not isinstance(args.trash, str):
            raise TypeError(f'Trash directory {args.trash} is not a string')
    if args.attachmentpath:
        if not isinstance(args.attachmentpath, str):
            raise TypeError(f'Attachment directory {args.attachmentpath} is not a string')

    # Obsidian Vault
    v = obs_vault.ObsVault(args.vaultroot)

    # If --attachmentpath is used, override the default
    if args.attachmentpath:
        v.attachmentdirs = [args.attachmentpath]
    logger.debug(f'Attachment directory(ies): {v.attachmentdirs}')

    # Compile list of all attachments in the vault
    all_attach: List[str] = v.allattachments

    # Compile list of all [[link]] targets in every doc in the vault
    all_link_tgts: Optional[List[str]] = []
    for d in v.docs:
        all_link_tgts.extend(d.internal_links)
    logger.debug(f'Found {len(all_link_tgts)} internal links in {len(v.docs)} documents')

    # Create list of files to delete (items from all_attach not in all_link_tgts)
    todelete: Optional[List[str]] = []
    for a in all_attach:
        if os.path.basename(a) not in all_link_tgts:
            todelete.append(a)
    logger.debug(f'Delete list contains {len(todelete)} file(s)')

    # By default, just list files to delete (as YAML list) on stdout
    if (not args.trash) and (not args.delete):
        logger.debug(f'Writing YAML-formatted deletion list to stdout')
        sys.stdout.write('delete:\n')
        for fp in todelete:
            sys.stdout.write(f'  - {fp}\n')

    # The "--trash DIR" option specifies that DIR be used as 'trash' and files moved there
    if args.trash:
        logger.debug(f'Creating trash dir at {args.trash} and moving deletable files into it')
        for fp in todelete:
            newfp = f'{args.trash.rstrip(os.sep)}{os.sep}{os.path.basename(fp)}'
            pathlib.Path(os.path.dirname(newfp)).mkdir(parents=True, exist_ok=True)  # create trash dir if needed
            logger.debug(f'Moving: {fp} -> {newfp}')
            shutil.move(fp, newfp)

    if args.delete:  # TODO: Implement --delete feature, which actually deletes files
        raise NotImplementedError


if __name__ == '__main__':
    sys.exit(main())

