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
punct_translator = str.maketrans('', '', string.punctuation)


class NameType(Enum):
    PERSONAL = 'personal'
    CORPORATE = 'corporate'
    FAMILY = 'family'
    OTHER = 'other'


class RoleTerm(Enum):
    PHOTOGRAPHER = 'photographer'


class TitleType(Enum):
    FULL = 'full'
    SHORT = 'short'
    SUBTITLE = 'subtitle'
    TRANSLATED = 'translated'


class LanguageAware:
    """Superclass for providing language awareness to other classes."""

    def __init__(self, lang: str = 'und', **kwargs):
        tag = language_tags.tags.check(lang)
        if not tag:
            raise ValueError(
                'Invalid language tag: "{}"'.format(tag))
        self.lang = lang


class SortAware:
    """Superclass for providing sortability information to other classes."""

    def __init__(self, sort_val: str, force: bool = False, **kwargs):
        logger.debug('sort_val: "{}"'.format(sort_val))
        logger.debug('force: {}'.format(force))
        if force:
            self.sort_val = sort_val
        else:
            self.sort_val = sort_val.translate(punct_translator).lower().\
                            replace(' ', '')


class Name(LanguageAware, SortAware):

    def __init__(
        self,
        full_name: str,
        display_name: str = '',
        name_type: NameType = NameType.PERSONAL,
        **kwargs
    ) -> None:
        self.full_name = full_name
        if display_name != '':
            self.display_name = display_name
        else:
            self.display_name = full_name
        try:
            kwargs['sort_val']
        except KeyError:
            logger.debug('Name supplying sort_val')
            SortAware.__init__(self, sort_val=self.display_name)
        else:
            logger.debug('Forcing provided sort_val')
            SortAware.__init__(self, **kwargs, force=True)
        self.name_type = name_type
        LanguageAware.__init__(self, **kwargs)

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


class Title(LanguageAware, SortAware):

    def __init__(
        self,
        title_val: str,
        title_type: TitleType = TitleType.FULL,
        **kwargs
    ):
        self.value = title_val
        self.title_type = title_type
        try:
            kwargs['sort_val']
        except KeyError:
            SortAware.__init__(self, sort_val=self.value)
        else:
            SortAware.__init__(self, **kwargs, force=True)
        LanguageAware.__init__(self, **kwargs)


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

