# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

__title__ = 'constrtuct_cpenv'
__description__ = 'Construct Cpenv Integration'
__version__ = '0.0.1'
__author__ = 'Dan Bradham'
__email__ = 'danielbradham@gmail.com'
__license__ = 'MIT'
__url__ = 'https://github.com/danbradham/constrtuct_cpenv'

from construct_cpenv.actions import *
from construct_cpenv import launcher


def available(ctx):
    return True


def register(cons):
    '''Register Launch Actions from Project Configuration'''

    CpenvSet.register(cons)
    CpenvList.register(cons)
    CpenvShow.register(cons)
    CpenvShell.register(cons)
    launcher.register(cons)


def unregister(cons):
    '''Unregister Launch Actions'''

    launcher.unregister(cons)
    CpenvShell.unregister(cons)
    CpenvShow.unregister(cons)
    CpenvList.unregister(cons)
    CpenvSet.unregister(cons)
