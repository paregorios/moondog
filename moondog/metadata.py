#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metadata management for moondog
"""

import better_exceptions
from enum import Enum, auto
import inspect
import json
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


class GetDict(object):
    """Superclass for dictionary serialization."""

    def __init__(self):
        pass

    def get_dict(self) -> dict:
        members = inspect.getmembers(self, lambda a: not(inspect.isroutine(a)))
        members = [a for a in members if (
            not(a[0].startswith('__') and a[0].endswith('__')))]
        d = {}
        for name, value in members:
            if isinstance(value, str):
                d[name] = value
            elif isinstance(value, list):
                d[name] = []
                for i, item in enumerate(value):
                    if type(item) in [Agent, Name, Title]:
                        d[name].append(item.get_dict())
                    else:
                        raise NotImplementedError(
                            'no way: {}'.format(type(item)))
            elif type(value) in [NameType, RoleTerm, TitleType]:
                d[name] = value.value
            else:
                raise NotImplementedError('nope')
        return d


class LanguageAware(object):
    """Superclass for providing language awareness to other classes."""

    def __init__(self, lang: str = 'und', **kwargs):
        tag = language_tags.tags.check(lang)
        if not tag:
            raise ValueError(
                'Invalid language tag: "{}"'.format(tag))
        self.lang = lang


class SortAware(object):
    """Superclass for providing sortability information to other classes."""

    def __init__(self, sort_val: str, force: bool = False, **kwargs):
        logger.debug('sort_val: "{}"'.format(sort_val))
        logger.debug('force: {}'.format(force))
        if force:
            self.sort_val = sort_val
        else:
            self.sort_val = sort_val.translate(punct_translator).lower().\
                            replace(' ', '')
        logger.debug('resulting sort_val: "{}"'.format(self.sort_val))


class Name(LanguageAware, SortAware, GetDict):

    def __init__(
        self,
        full_name: str,
        display_name: str = '',
        name_type: NameType = NameType.PERSONAL,
        **kwargs
    ) -> None:
        logger.debug('boom')
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


class Agent(GetDict):

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


class Title(LanguageAware, SortAware, GetDict):

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


class DescriptiveMetadata(GetDict):

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
        self.titles = []
        try:
            kwargs['titles']
        except KeyError:
            pass
        else:
            for t in kwargs['titles']:
                if isinstance(t, Title):
                    self.titles.append(t)
                elif isinstance(t, dict):
                    self.titles.append(Title(**t))
                else:
                    raise ValueError(
                        'Title information of type {} is not supported.'
                        ''.format(type(a)))

    def write_json(self, path: str):
        d = self.get_dict()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=4, sort_keys=True)
        del f
