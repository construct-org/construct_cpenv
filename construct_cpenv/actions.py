# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

__all__ = [
    'CpenvSet',
    'CpenvShow',
    'CpenvList',
    'CpenvShell'
]

import os
import subprocess
import fsfs
from construct import Action, types


class CpenvSet(Action):
    '''Sets the cpenv modules to activate on launch for current context'''

    label = 'Set cpenv'
    identifier = 'cpenv.set'

    @staticmethod
    def parameters(ctx):
        params = dict(
            root={
                'label': 'Root',
                'required': True,
                'type': types.Entry,
                'help': 'Root directory to set cpenv modules for',
            },
            modules={
                'label': 'Modules',
                'required': True,
                'type': types.String,
                'help': 'Space separated list of cpenv modules'
            }
        )

        if not ctx:
            return params

        entry = ctx.get_deepest_entry()
        params['root']['default'] = entry or fsfs.get_entry(os.getcwd())

        return params

    @staticmethod
    def available(ctx):
        return ctx.host == 'cli' and ctx.project


class CpenvShow(Action):
    '''Shows the cpenv modules that will be activated'''

    label = 'Show cpenv'
    identifier = 'cpenv.show'

    @staticmethod
    def parameters(ctx):
        params = dict(
            root={
                'label': 'Root',
                'required': True,
                'type': fsfs.Entry,
                'help': 'Root directory to show cpenv modules for',
            }
        )

        if not ctx:
            return params

        entry = ctx.get_deepest_entry()
        params['root']['default'] = entry or fsfs.get_entry(os.getcwd())

        return params

    @staticmethod
    def available(ctx):
        return ctx.host == 'cli' and ctx.project


class CpenvList(Action):
    '''Lists the available cpenv modules'''

    label = 'List cpenv modules'
    identifier = 'cpenv.list'
    suppress_signals = True

    @staticmethod
    def available(ctx):
        return ctx.host == 'cli' and ctx.project


class CpenvShell(Action):
    '''Activates a cpenv subshell'''

    label = 'Cpenv Subshell'
    identifier = 'cpenv.shell'

    @staticmethod
    def parameters(ctx):
        params = dict(
            root={
                'label': 'Root',
                'required': True,
                'type': fsfs.Entry,
                'help': 'Root directory to set cpenv modules for',
            }
        )

        if ctx:
            entry = ctx.get_deepest_entry()
            params['root']['default'] = entry or fsfs.get_entry(os.getcwd())

        return params

    @staticmethod
    def available(ctx):
        return ctx.host == 'cli' and ctx.project


class CpenvEdit(Action):
    '''Open existing .cpenv file or create a new one.'''

    label = 'Edit .cpenv file'
    identifier = 'cpenv.edit'

    @staticmethod
    def parameters(ctx):
        params = dict(
            root={
                'label': 'Root',
                'required': True,
                'type': types.Entry,
                'help': 'Root directory to set cpenv modules for',
            }
        )

        if not ctx:
            return params

        entry = ctx.get_deepest_entry()
        params['root']['default'] = entry or fsfs.get_entry(os.getcwd())

        return params

    @staticmethod
    def available(ctx):
        return ctx.host == 'cli' and ctx.project

