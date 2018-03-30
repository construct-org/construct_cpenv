# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
__all__ = [
    'activate_cpenv',
    'activate_cpenv_modules',
    'get_cpenv',
    'launch_cpenv_shell',
    'list_cpenv_modules',
    'show_cpenv',
    'validate_cpenv_modules',
    'write_cpenv_modules',
]

import os
from construct.tasks import (
    task,
    pass_context,
    requires,
    success,
    returns,
    store,
    params,
    kwarg,
    pass_args,
    artifact
)
from construct.errors import Fail


@task
@params(kwarg('modules'))
@returns(store('cpenv_resolver'))
def validate_cpenv_modules(modules):
    '''Validate cpenv modules'''

    import cpenv
    modules = modules.split()
    return cpenv.resolve(*modules)


@task
@requires(success('validate_cpenv_modules'))
@params(kwarg('root'), store('cpenv_resolver'))
@returns(artifact('cpenv_file'))
def write_cpenv_modules(root, resolver):
    '''Write a cpenv file to root'''

    resolver_str = ' '.join([obj.name for obj in resolver.resolved])
    cpenv_file = os.path.join(root.path, '.cpenv').replace('\\', '/')
    with open(cpenv_file, 'w') as f:
        f.write(resolver_str)
    return cpenv_file


@task
@params(kwarg('root'))
@returns(store('cpenv_resolver'))
def get_cpenv(root):
    '''Resolve cpenv modules for the given path'''

    import cpenv
    import cpenv.resolver
    try:
        return cpenv.resolve(root.path)
    except cpenv.resolver.ResolveError as e:
        raise Fail(e)


@task
@requires(success('get_cpenv'))
@params(store('cpenv_resolver'))
@returns(artifact('cpenv_modules'))
def show_cpenv(resolver):
    '''Return a list of cpenv module names'''

    import cpenv.cli as cpenv_cli
    modules = sorted(resolver.resolved, key=cpenv_cli._type_and_name)
    return ' '.join([obj.name for obj in modules])


@task
@requires(success('get_cpenv'))
@params(store('cpenv_resolver'))
def activate_cpenv(resolver):
    '''Activate cpenv modules'''

    resolver.activate()


@task
def list_cpenv_modules():
    '''Print cpenv environments and modules'''

    import cpenv
    from cpenv.cli import format_objects

    environments = cpenv.get_environments()
    modules = cpenv.get_modules()
    print(format_objects(environments + modules, children=True), end='\n\n')


@task
@requires(success('get_cpenv'))
@params(store('cpenv_resolver'))
def launch_cpenv_shell(resolver):

    import cpenv
    import cpenv.shell
    import cpenv.cli
    resolved = set(resolver.resolved)

    active_modules = set()
    env = cpenv.get_active_env()
    if env:
        active_modules.add(env)
    active_modules.update(cpenv.get_active_modules())

    resolver.activate()
    modules = sorted(resolved | active_modules, key=cpenv.cli._type_and_name)
    prompt = ':'.join([obj.name for obj in modules])
    cpenv.shell.launch(prompt)


# Launcher Task
from construct_launcher import BEFORE_LAUNCH

@task
@requires(success('build_app_env'), success('get_cpenv'))
@params(store('app'), store('cpenv_resolver'))
def activate_cpenv_modules(app, resolver):
    '''Add cpenv modules to app env'''

    import cpenv
    import cpenv.utils as utils

    r = cpenv.resolve(app.cwd)
    cpenv_env = r.combine()
    app_env = utils.env_to_dict(app.env)
    combined_env = utils.join_dicts(app_env, cpenv_env)
    app.env = utils.dict_to_env(combined_env)
