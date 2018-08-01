#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for moondog """

import logging
from moondog.images import Image as MoondogImage
from nose.tools import assert_equal, assert_false, assert_true, raises
from os import makedirs
from os.path import abspath, exists, join, realpath
from shutil import rmtree
from unittest import TestCase

logger = logging.getLogger(__name__)
test_data_path = abspath(realpath(join('tests', 'data')))
test_bag_path = join(test_data_path, 'foo')


def setup_module():
    """Change me"""
    pass


def teardown_module():
    """Change me"""
    pass


class Test_Image_Basics(TestCase):

    def setUp(self):
        """Change me"""
        if exists(test_bag_path):
            rmtree(test_bag_path)

    def tearDown(self):
        """Delete temporary items"""
        if exists(test_bag_path):
            rmtree(test_bag_path)

    def test_image_construct(self):
        """Test Image Construction"""
        im = MoondogImage(test_bag_path, auto_make=True)
        assert_true(isinstance(im, MoondogImage))
        del im

    @raises(OSError)
    def test_image_construct_exists(self):
        makedirs(test_bag_path)
        im = MoondogImage(test_bag_path, auto_make=True)
        del im

    @raises(OSError)
    def test_image_construct_fail(self):
        """Test Image Construction Failure (does not exist)"""
        im = MoondogImage(test_bag_path)  # default: auto_make=False
        del im

