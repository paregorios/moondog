#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for moondog """

from bagit import BagError
import logging
from moondog.images import ImageBag
from nose.tools import assert_equal, assert_false, assert_true, raises
from os import makedirs
from os.path import abspath, exists, join, realpath
from shutil import rmtree
import sys
from unittest import TestCase

logger = logging.getLogger(__name__)
test_data_path = abspath(realpath(join('tests', 'data')))
test_bag_path = join(test_data_path, 'foo')
test_original = 'IMG_4107.JPG'
test_original_path = join(test_bag_path, 'data', test_original)
test_master_path = join(test_bag_path, 'data', 'master.tif')


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
        im = ImageBag(test_bag_path, auto_make=True)
        assert_true(isinstance(im, ImageBag))
        del im

    @raises(OSError)
    def test_image_construct_exists(self):
        makedirs(test_bag_path)
        im = ImageBag(test_bag_path, auto_make=True)
        del im

    @raises(OSError)
    def test_image_construct_fail(self):
        """Test Image Construction Failure (does not exist)"""
        im = ImageBag(test_bag_path)  # default: auto_make=False
        del im


class Test_Image_Import(TestCase):

    def setUp(self):
        """Change me"""
        if exists(test_bag_path):
            rmtree(test_bag_path)

    def tearDown(self):
        """Change me"""
        if exists(test_bag_path):
            rmtree(test_bag_path)

    def test_import(self):
        im = ImageBag(test_bag_path, auto_make=True)
        im.accession(join(test_data_path, 'src', 'IMG_4107.JPG'))
        assert_true(exists(test_original_path))
        assert_true(exists(test_master_path))
        with open(join(test_bag_path, 'bag-info.txt'), 'r') as f:
            lines = [l[:-1] for l in f.readlines()]
        del f
        for line in lines:
            print(line)
        assert_true(lines[0].startswith("Bag-Software-Agent: bagit.py"))
        assert_true(lines[1].startswith("Bagging-Date: "))
        assert_equal(lines[2], "Master-Filename: master.tif")
        assert_true(lines[3].startswith("Original-Accession-Path:"))
        assert_equal(lines[4], "Original-Filename: IMG_4107.JPG")
        assert_true(exists(join(test_data_path, 'src', 'IMG_4107.JPG')))

