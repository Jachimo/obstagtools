# Part of 'Obsidian Tag Tools': https://github.com/Jachimo/obstagtools
# Requires Python 3.5+, tested using Python 3.9

import os
import logging
from typing import List, Optional

import obs_document
import obs_config as config


# LOGGING
logger = logging.getLogger(__name__)


class ObsVault(object):
    def __init__(self, path: str):
        self.root = path
        self.attachmentdirs = config.ATTACHMENT_DIRS

    @property
    def root(self) -> str:
        return self._rootpath

    @root.setter
    def root(self, path: str) -> None:
        strippedpath = path.rstrip(os.sep)
        if not os.path.isdir(strippedpath):
            raise ValueError(f'Vault root must be a directory; "{strippedpath}" does not appear to be.')
        self._rootpath = strippedpath

    @property
    def doclist(self) -> List[str]:
        docs: Optional[List[str]] = []
        for root, dirs, files in os.walk(self.root):
            for f in files:
                if any(s in root for s in config.SKIP_DIRS):  # don't add files from SKIP_DIRS
                    continue
                elif any(s in root for s in config.ATTACHMENT_DIRS):  # or ATTACHMENT_DIRS
                    continue
                elif f.split('.')[-1] in config.ALLOWED_FILE_EXTENSIONS:
                    docs.append(f'{root}{os.sep}{f}')
        logger.debug(f'Vault {os.path.basename(self.root)} contains {len(docs)} docs')
        return docs

    @property
    def docs(self) -> list:  # when in sep file, List[ObsDocument]
        dl = []
        for d in self.doclist:
            dl.append(obs_document.ObsDocument(d))
        return dl

    @property
    def attachmentdirs(self) -> List[str]:
        return self._attachmentdirs

    @attachmentdirs.setter
    def attachmentdirs(self, paths: List[str]) -> None:
        apaths: Optional[List[str]] = []
        for p in paths:
            apath = self.root + os.sep + p.rstrip(os.sep)
            if not os.path.isdir(apath):
                raise ValueError(f'Specified attachment directory "{apath}" not found or not a directory.')
            else:
                apaths.append(apath)
        self._attachmentdirs = apaths

    @property
    def allattachments(self) -> List[str]:
        aps: Optional[List[str]] = []
        for d in config.ATTACHMENT_DIRS:
            for root, subdirs, files in os.walk(f'{self.root.rstrip(os.sep)}{os.sep}{d}'):
                for f in files:
                    aps.append(f'{root}{os.sep}{f}')
        logger.debug(f'Vault {os.path.basename(self.root)} contains {len(aps)} attachments')
        return aps
