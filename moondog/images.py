#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manage image collection
"""

from bagit import Bag, BagError, make_bag
import better_exceptions
import logging
from os import makedirs
from os.path import expanduser, expandvars, normpath, realpath

logger = logging.getLogger(__name__)


class Image:

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
        return None
