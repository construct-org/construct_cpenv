# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

__all__ = [
    'activate_cpenv_modules',
    'register',
    'unregister',
]

import os
import subprocess
from construct_launcher import BEFORE_LAUNCH
from construct import (
    context,
    to_env_dict,
    task,
    requires,
    success,
    params,
    store,
    returns
)


@task(priority=BEFORE_LAUNCH)
@requires(success('build_app_env'))
@params(store('app'))
@returns(store('app'))
def activate_cpenv_modules(app):

    import cpenv
    import cpenv.utils as utils

    r = cpenv.resolve(app['cwd'])
    cpenv_env = r.combine()
    app_env = utils.env_to_dict(app['env'])
    env = utils.join_dicts(app_env, cpenv_env)
    app['env'] = utils.dict_to_env(env)
    return app


def register(cons):

    cons.action_hub.connect('launch.*', activate_cpenv_modules)


def unregister(cons):

    cons.action_hub.disconnect('launch.*', activate_cpenv_modules)
