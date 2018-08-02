#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metadata management for moondog
"""

import better_exceptions
from enum import Enum, auto
import language_tags
import logging
# from lxml import etree
from os.path import (basename, expanduser, expandvars, join, normpath,
                     realpath, splitext)
import string
from validators import url

logger = logging.getLogger(__name__)


class NameType(Enum):
    PERSONAL = 'personal'
    CORPORATE = 'corporate'
    FAMILY = 'family'
    OTHER = 'other'


class RoleTerm(Enum):
    PHOTOGRAPHER = 'photographer'


class Name:

    def __init__(
        self,
        full_name: str,
        display_name: str = '',
        sort_name: str = '',
        name_type: NameType = NameType.PERSONAL,
        lang: str = 'und'
    ) -> None:
        self.full_name = full_name
        if display_name != '':
            self.display_name = display_name
        else:
            self.display_name = full_name
        if sort_name != '':
            translator = str.maketrans('', '', string.punctuation)
            self.sort_name = sort_name.translate(translator).lower().replace(
                ' ', '')
        else:
            self.sort_name = self.full_name.lower().replace(' ', '')
        self.name_type = name_type
        tag = language_tags.tags.tag(lang)
        if tag is None:
            raise ValueError(
                'Invalid language tag: "{}"'.format(tag))
        self.lang = lang

    def __str__(self):
        return '{} name: "{}"'.format(self.name_type.value, self.full_name)


class Agent:

    def __init__(
        self,
        names: list,
        role: RoleTerm = RoleTerm.PHOTOGRAPHER,
        uris: list = None
    ) -> None:
        self.names = []
        for name in names:
            if isinstance(name, Name):
                self.names.append(name)
            elif isinstance(name, dict):
                self.names.append(Name(**name))
            else:
                raise ValueError(
                    'Name information of type {} is not supported.'
                    ''.format(type(name)))
        self.role = role
        self.uris = []
        if uris is not None:
            for uri in uris:
                if url(uri):
                    self.uris.append(uri)
                else:
                    raise ValueError(
                        'URI value is not valid: "{}"'
                        ''.format(uri))

    def __str__(self):
        return '{}: {}'.format(self.role.value, self.names[0].full_name)


class DescriptiveMetadata:

    def __init__(self, **kwargs):
        self.agents = []
        try:
            kwargs['agents']
        except KeyError:
            pass
        else:
            for a in kwargs['agents']:
                if isinstance(a, Agent):
                    self.agents.append(a)
                elif isinstance(a, dict):
                    self.agents.append(Agent(**a))
                else:
                    raise ValueError(
                        'Agent information of type {} is not supported.'
                        ''.format(type(a)))

