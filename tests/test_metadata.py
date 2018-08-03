#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test metadata functionality for moondog"""

import logging
from moondog.metadata import (Agent, LanguageAware, Name, DescriptiveMetadata,
                              NameType, RoleTerm, Title, TitleType)
from nose.tools import assert_dict_equal, assert_equal, assert_false, assert_true, raises
from os.path import abspath, join, realpath
from unittest import TestCase

logger = logging.getLogger(__name__)
test_data_path = abspath(realpath(join('tests', 'data')))

TestCase.maxDiff = None


def setup_module():
    """Change me"""
    pass


def teardown_module():
    """Change me"""
    pass


class Test_Metadata(TestCase):

    maxDiff = None

    def setUp(self):
        """Change me"""
        pass

    def tearDown(self):
        """Change me"""
        pass

    def test_languageaware(self):
        LanguageAware(lang='fr')

    @raises(ValueError)
    def test_languageaware_bad(self):
        LanguageAware(lang="bad_apples")

    def test_name(self):
        """Test name creation"""
        d = {
            'full_name': 'Tom Elliott',
            'display_name': 'Elliott, Tom',
            'name_type': NameType.PERSONAL,
            'lang': 'en'
        }
        n = Name(**d)
        assert_equal(n.full_name, 'Tom Elliott')
        assert_equal(n.display_name, 'Elliott, Tom')
        assert_equal(n.sort_val, 'elliotttom')
        assert_equal(n.name_type, NameType.PERSONAL)
        assert_equal(n.lang, 'en')
        assert_equal(str(n), 'personal name: "Tom Elliott"')

    def test_name_auto(self):
        """Test name automatic defaults."""
        d = {'full_name': 'Tom Elliott'}
        n = Name(**d)
        assert_equal(n.sort_val, 'tomelliott')  # yeah, it's not very smart

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
        names = [{'full_name': 'Tom Elliott', 'sort_val': 'elliotttom'}]
        a = Agent(names)
        assert_equal(a.names[0].full_name, 'Tom Elliott')
        assert_equal(a.names[0].sort_val, 'elliotttom')
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

    def test_title(self):
        """Test title"""
        d = {
            'title_val': 'Rocks: Thinking Things',
            'title_type': TitleType.FULL
        }
        t = Title(**d)
        assert_equal(t.value, 'Rocks: Thinking Things')
        assert_equal(t.sort_val, 'rocksthinkingthings')
        assert_equal(t.title_type, TitleType.FULL)
        del t
        d['sort_val'] = '12345'
        t = Title(**d)
        assert_equal(t.sort_val, '12345')

    def test_descriptive_metadata(self):
        """Test descriptive metadata"""
        m = DescriptiveMetadata(
            agents=[Agent(names=[Name('Tom Elliott')])],
            titles=[Title('A quick trip to Zucchabar')])
        assert_equal(str(m.agents[0]), 'photographer: Tom Elliott')
        assert_equal(m.titles[0].value, 'A quick trip to Zucchabar')
        assert_equal(m.titles[0].sort_val, 'aquicktriptozucchabar')

    def test_descriptive_metadata_agent_dict(self):
        """Test descriptive metadata with agent info in a dict"""
        m = DescriptiveMetadata(agents=[{'names': [Name('Tom Elliott')]}])
        assert_equal(str(m.agents[0]), 'photographer: Tom Elliott')

    @raises(ValueError)
    def test_descriptive_metadata_agent_bad(self):
        """Test descriptive metadata with badly formated agent."""
        m = DescriptiveMetadata(agents=['the', 'long', 'and', 'winding'])
        del m

    def test_descriptive_metadata_title_dict(self):
        """Test descriptive metadata with title info in a dict"""
        m = DescriptiveMetadata(
            agents=[{'names': [Name('Tom Elliott')]}],
            titles=[{'title_val': 'A quick trip to Zucchabar'}])
        assert_equal(str(m.agents[0]), 'photographer: Tom Elliott')
        assert_equal(m.titles[0].value, 'A quick trip to Zucchabar')

    @raises(ValueError)
    def test_descriptive_metadata_title_bad(self):
        """Test descriptive metadata with badly formatted title"""
        m = DescriptiveMetadata(
            agents=[{'names': [Name('Tom Elliott')]}],
            titles=['the', 'road', 'goes', 'ever', 'ever', 'on'])
        del m

    def test_descriptive_metadata_no_agents(self):
        """Test descriptive metadata without agents"""
        m = DescriptiveMetadata(**{})
        del m

    def test_descriptive_metadata_get_dict(self):
        n = Name('Tom Elliott')
        assert_equal(n.display_name, 'Tom Elliott')
        assert_equal(n.sort_val, 'tomelliott')
        m = DescriptiveMetadata(
            agents=[Agent(names=[n])],
            titles=[Title('A quick trip to Zucchabar')])
        d = m.get_dict()
        assert_dict_equal(
            d,
            {
                'agents': [
                    {
                        'names': [
                            {
                                'full_name': 'Tom Elliott',
                                'display_name': 'Tom Elliott',
                                'sort_val': 'tomelliott',
                                'name_type': 'personal',
                                'lang': 'und'
                            }
                        ],
                        'role': 'photographer',
                        'uris': []
                    }
                ],
                'titles': [
                    {
                        'sort_val': 'aquicktriptozucchabar',
                        'lang': 'und',
                        'title_type': 'full',
                        'value': 'A quick trip to Zucchabar',
                    }
                ]
            })

    def test_descriptive_metadata_write_json(self):
        m = DescriptiveMetadata(
            agents=[Agent(names=[Name('Tom Elliott')])],
            titles=[Title('A quick trip to Zucchabar')])
        m.write_json(join(test_data_path, 'zucchabar.json'))


