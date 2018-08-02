#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manage image collection
"""

from bagit import Bag, BagError, make_bag
import better_exceptions
from exiftool import ExifTool
from libxmp import XMPFiles
import logging
from os import makedirs
from os.path import (basename, expanduser, expandvars, join, normpath,
                     realpath, splitext)
from PIL import Image
from pprint import pprint
import shutil

logger = logging.getLogger(__name__)


class ImageBag:

    def __init__(self, path: str, auto_make: bool = False) -> None:
        self.path = realpath(expanduser(expandvars(normpath(path))))
        if auto_make:
            try:
                makedirs(self.path, exist_ok=False)
            except OSError:
                raise OSError(
                    '{} already exists, but auto_make = True'
                    ''.format(self.path))
            else:
                self.bag = make_bag(self.path)
        else:
            try:
                self.bag = Bag(self.path)
            except BagError as e:
                raise OSError(
                    '{} does not seem to be a valid Moondog Image bag: {}'
                    ''.format(self.path, str(e)))
        self.components = {}
        return None

    def accession(self, path: str):
        self._import_original(path)
        self._generate_master()

    def _import_original(self, path: str):
        d = self.components['original'] = {}
        d['accession_path'] = realpath(expanduser(expandvars(normpath(path))))
        d['filename'] = basename(d['accession_path'])
        fn, ext = splitext(d['filename'])
        target_path = join(self.path, 'data', d['filename'])
        shutil.copy2(
            d['accession_path'], target_path)
        with ExifTool() as et:
            meta = et.get_metadata(target_path)
        pprint(meta)
        xmp = XMPFiles(file_path=target_path).get_xmp()
        pprint(xmp)
        self._update(manifests=True)

    def _generate_master(self):
        infn = self.components['original']['filename']
        d = self.components['master'] = {}
        d['filename'] = 'master.tif'
        Image.open(
            join(self.path, 'data', infn)).save(
            join(self.path, 'data', d['filename']))
        self._update(manifests=True)

    def _update(self, manifests=False):
        """Update the bag."""
        for fn, fmeta in self.components.items():
            for term, value in fmeta.items():
                bag_term = '{}-{}'.format(
                    fn.title(),
                    term.replace('_', ' ').title().replace(' ', '-'))
                try:
                    prior_value = self.bag.info[bag_term]
                except KeyError:
                    self.bag.info[bag_term] = value
                else:
                    if prior_value != value:
                        self.bag.info[bag_term] = value
        self.bag.save(manifests=manifests)

