# -*- coding: utf-8 -*-
from __future__ import absolute_import

__all__ = ['Cpenv']

import os
import fsfs
from construct.extension import Extension
from construct_cpenv.tasks import (
    activate_cpenv,
    activate_cpenv_modules,
    get_cpenv,
    launch_cpenv_shell,
    list_cpenv_modules,
    show_cpenv,
    validate_cpenv_modules,
    write_cpenv_modules,
    edit_cpenv_modules,
)
from construct_cpenv.actions import (
    CpenvSet,
    CpenvShow,
    CpenvList,
    CpenvShell,
    CpenvEdit,
)


class Cpenv(Extension):
    '''Integrates cpenv with construct.

    cpenv is used to manage python virtualenvs and bundles of config called
    modules. This extension provides cli Actions for setting the cpenv modules
    that construct should activate in that location. Additionally, a task is
    added to cpenv_launcher's launch.* actions that activates cpenvmodules
    before launching any software.
    '''

    name = 'cpenv'
    attr_name = 'cpenv'

    def available(self, ctx):
        return True

    def load(self):

        # cli actions
        self.add_action(CpenvSet)
        self.add_task(CpenvSet, validate_cpenv_modules)
        self.add_task(CpenvSet, write_cpenv_modules)

        self.add_action(CpenvShow)
        self.add_task(CpenvShow, get_cpenv)
        self.add_task(CpenvShow, show_cpenv)

        self.add_action(CpenvList)
        self.add_task(CpenvList, list_cpenv_modules)

        self.add_action(CpenvShell)
        self.add_task(CpenvShell, get_cpenv)
        self.add_task(CpenvShell, launch_cpenv_shell)

        self.add_action(CpenvEdit)
        self.add_task(CpenvEdit, edit_cpenv_modules)

        # Extend cpenv_launcher to activate cpenv modules before launch
        from construct_launcher.constants import BEFORE_LAUNCH
        self.add_task(
            'launch.*',
            get_cpenv,
            arg_getters=[
                lambda ctx: ctx.get_deepest_entry()
                or fsfs.get_entry(os.getcwd())
            ],
            priority=BEFORE_LAUNCH,
        )
        self.add_task(
            'launch.*',
            activate_cpenv_modules,
            priority=BEFORE_LAUNCH,
        )
