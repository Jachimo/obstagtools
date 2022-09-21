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
        if not path:
            raise ValueError(f'Vault root cannot be null/None')
        if not isinstance(path, str):
            raise TypeError(f'Vault path must be a string, "{path}" (type {type(path)}) passed')
        strippedpath = path.rstrip(os.sep)
        if not os.path.isdir(strippedpath):
            raise ValueError(f'Vault root must be a directory; "{strippedpath}" does not appear to be.')
        self._rootpath = strippedpath

    @property
    def doclist(self) -> List[str]:
        docs: List[str] = []
        root: str
        dirs: List[str]
        files: List[str]
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
    def docs(self) -> List[obs_document.ObsDocument]:
        dl: list = []
        for d in self.doclist:
            dl.append(obs_document.ObsDocument(d))
        return dl

    @property
    def attachmentdirs(self) -> Optional[List[str]]:
        return self._attachmentdirs

    @attachmentdirs.setter
    def attachmentdirs(self, paths: Optional[List[str]]) -> None:
        if not paths:  # attachmentdirs SHOULD be able to be None under some circumstances (not required)
            logger.debug(f'Setting attachment directories for {self.root} to None; this may cause problems.')
            self._attachmentdirs = None
            return None
        assert paths is not None

        extpaths: List[str] = []
        p: str
        for p in paths:
            rootedpath: str = self.root + os.sep + p.rstrip(os.sep)  # self.root has already been .rstripped
            if not os.path.isdir(rootedpath):
                raise ValueError(f'Specified attachment directory "{rootedpath}" not found or not a directory.')
            else:
                extpaths.append(rootedpath)
        self._attachmentdirs = extpaths
        assert self._attachmentdirs is not None

    @property
    def allattachments(self) -> Optional[List[str]]:
        if not config.ATTACHMENT_DIRS:
            logger.debug(f'config.ATTACHMENT_DIRS not specified for {self.root}')
            return None
        attach_list: list = []
        for d in config.ATTACHMENT_DIRS:
            for root, subdirs, files in os.walk(f'{self.root.rstrip(os.sep)}{os.sep}{d}'):
                for f in files:
                    attach_list.append(f'{root}{os.sep}{f}')
        logger.debug(f'Vault {os.path.basename(self.root)} contains {len(attach_list)} attachments')
        return attach_list
