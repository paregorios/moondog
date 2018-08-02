#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test metadata functionality for moondog"""

import logging
from moondog.metadata import Agent, Name, NameType, RoleTerm
from nose.tools import assert_equal, assert_false, assert_true, raises
from os.path import abspath, join, realpath
from unittest import TestCase

logger = logging.getLogger(__name__)
test_data_path = abspath(realpath(join('tests', 'data')))


def setup_module():
    """Change me"""
    pass


def teardown_module():
    """Change me"""
    pass


class Test_Metadata(TestCase):

    def setUp(self):
        """Change me"""
        pass

    def tearDown(self):
        """Change me"""
        pass

    def test_name(self):
        """Test name creation"""
        d = {
            'full_name': 'Tom Elliott',
            'display_name': 'Elliott, Tom',
            'sort_name': 'Elliott, Tom',
            'name_type': NameType.PERSONAL,
            'lang': 'en'
        }
        n = Name(**d)
        assert_equal(n.full_name, 'Tom Elliott')
        assert_equal(n.display_name, 'Elliott, Tom')
        assert_equal(n.sort_name, 'elliotttom')
        assert_equal(n.name_type, NameType.PERSONAL)
        assert_equal(n.lang, 'en')
        assert_equal(str(n), 'personal name: "Tom Elliott"')

    def test_agent(self):
        """Test agent creation"""
        names = [Name('Tom Elliott')]
        a = Agent(names, uris=['http://orcid.org/0000-0002-4114-6677'])
        assert_equal(a.names[0].full_name, 'Tom Elliott')
        assert_equal(a.role, RoleTerm.PHOTOGRAPHER)
        assert_equal(a.uris[0], 'http://orcid.org/0000-0002-4114-6677')
        assert_equal(str(a), 'photographer: Tom Elliott')

    def test_agent_name_dict(self):
        """Test agent creation with a dictionary for name"""
        names = [{'full_name': 'Tom Elliott', 'sort_name': 'Elliott, Tom'}]
        a = Agent(names)
        assert_equal(a.names[0].full_name, 'Tom Elliott')
        assert_equal(a.names[0].sort_name, 'elliotttom')
        assert_equal(a.role, RoleTerm.PHOTOGRAPHER)
        assert_equal(str(a), 'photographer: Tom Elliott')

    @raises(ValueError)
    def test_agent_name_bad(self):
        """Test agent creation with a bogus object for name"""
        names = [['no', 'soup', 'for', 'you']]
        a = Agent(names)
        del a

    @raises(ValueError)
    def test_agent_bad_uri(self):
        """Test agent creation"""
        names = [Name('Tom Elliott')]
        a = Agent(names, uris=['pickles!'])
        del a