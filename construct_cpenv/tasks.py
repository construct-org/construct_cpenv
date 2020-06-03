# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
import os
import shlex
import subprocess

from construct.utils import platform
from construct.tasks import (
    artifact,
    kwarg,
    params,
    requires,
    returns,
    store,
    success,
    task,
)
from construct.errors import Fail


__all__ = [
    'activate_cpenv',
    'activate_cpenv_modules',
    'get_cpenv',
    'launch_cpenv_shell',
    'list_cpenv_modules',
    'show_cpenv',
    'validate_cpenv_modules',
    'write_cpenv_modules',
    'edit_cpenv_modules',
]


@task
@params(kwarg('root'))
def edit_cpenv_modules(root):
    '''Edit the current entry.'''

    editor = os.environ.get('EDITOR', 'subl --wait')
    cpenv_file = os.path.join(root.path, '.cpenv').replace('\\', '/')
    cmd = shlex.split(editor) + [cpenv_file]

    kwargs = {
        'stdout': subprocess.PIPE,
        'stderr': subprocess.STDOUT,
    }
    if platform == 'win':
        CREATE_NO_WINDOW = 0x08000000
        kwargs['creationflags'] = CREATE_NO_WINDOW

    subprocess.Popen(cmd, **kwargs)


@task
@params(kwarg('modules'))
@returns(store('cpenv_modules'))
def validate_cpenv_modules(modules):
    '''Validate cpenv modules'''

    import cpenv
    modules = modules.split()
    return cpenv.resolve(modules)


@task
@requires(success('validate_cpenv_modules'))
@params(kwarg('root'), store('cpenv_modules'))
@returns(artifact('cpenv_file'))
def write_cpenv_modules(root, modules):
    '''Write a cpenv file to root'''

    resolver_str = ' '.join([m.qual_name for m in modules])
    cpenv_file = os.path.join(root.path, '.cpenv').replace('\\', '/')
    with open(cpenv_file, 'w') as f:
        f.write(resolver_str)
    return cpenv_file


@task
@params(kwarg('root'))
@returns(store('cpenv_modules'))
def get_cpenv(root):
    '''Resolve cpenv modules for the given path'''

    import cpenv
    try:
        return cpenv.resolve([root.path])
    except cpenv.ResolveError as e:
        raise Fail(e)


@task
@requires(success('get_cpenv'))
@params(store('cpenv_modules'))
@returns(artifact('cpenv_modules'))
def show_cpenv(modules):
    '''Return a list of cpenv module names'''

    return ' '.join(sorted([m.qual_name for m in modules]))


@task
@requires(success('get_cpenv'))
@params(store('cpenv_modules'))
def activate_cpenv(modules):
    '''Activate cpenv modules'''

    import cpenv
    cpenv.activate([m.qual_name for m in modules])


@task
def list_cpenv_modules():
    '''Print cpenv environments and modules'''

    from cpenv import cli
    from cpenv.__main__ import List

    cli.run(List, [])


@task
@requires(success('get_cpenv'))
@params(store('cpenv_modules'))
def launch_cpenv_shell(modules):

    from cpenv import cli
    from cpenv.__main__ import Activate

    cli.run(Activate, [m.qual_name for m in modules])


@task
@requires(success('build_app_env'), success('get_cpenv'))
@params(store('app'), store('cpenv_modules'))
def activate_cpenv_modules(app, modules):
    '''Add cpenv modules to app env'''

    import cpenv
    from cpenv import mappings

    localizer = cpenv.Localizer(to_repo='home')
    localized = localizer.localize(modules)
    activator = cpenv.Activator(localizer)
    cpenv_env = activator.combine_modules(localized)

    app_env = mappings.env_to_dict(app.env)
    combined_env = mappings.join_dicts(app_env, cpenv_env)
    app.env = mappings.dict_to_env(combined_env)
