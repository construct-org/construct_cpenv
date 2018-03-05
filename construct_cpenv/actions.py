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
from construct import (
    Action,
    types,
    to_env_dict,
    task,
    requires,
    success,
    store,
    pass_context,
    pass_kwargs,
    params,
    kwarg,
    returns,
    artifact
)


class CpenvSet(Action):

    label = 'Set cpenv'
    identifier = 'cpenv.set'
    description = 'Sets the cpenv modules to activate on launch for current ctx'

    @staticmethod
    def parameters(ctx):
        params = dict(
            root={
                'label': 'Root',
                'required': True,
                'type': fsfs.Entry,
                'help': 'Root directory to set cpenv modules for',
            },
            modules={
                'label': 'Modules',
                'required': True,
                'type': str,
                'help': 'List of cpenv modules'
            }
        )

        if ctx:
            entry = ctx.get_deepest_entry()
            params['root']['default'] = entry or fsfs.get_entry(os.getcwd())

        return params

    @staticmethod
    def available(ctx):
        return ctx.host == 'cli'

    @classmethod
    def register(cls, cons):
        cons.action_hub.register(cls)
        cons.action_hub.connect(cls.identifier, validate_cpenv_modules)
        cons.action_hub.connect(cls.identifier, write_cpenv_modules)

    @classmethod
    def unregister(cls, cons):
        cons.action_hub.disconnect(cls.identifier, write_cpenv_modules)
        cons.action_hub.disconnect(cls.identifier, validate_cpenv_modules)
        cons.action_hub.unregister(cls)


@task
@params(kwarg('modules'))
@returns(store('cpenv_resolver'))
def validate_cpenv_modules(modules):
    import cpenv
    modules = modules.split()
    return cpenv.resolve(*modules)


@task
@requires(success('validate_cpenv_modules'))
@params(kwarg('root'), store('cpenv_resolver'))
@returns(artifact('cpenv_file'))
def write_cpenv_modules(root, resolver):

    resolver_str = ' '.join([obj.name for obj in resolver.resolved])
    cpenv_file = os.path.join(root.path, '.cpenv').replace('\\', '/')
    with open(cpenv_file, 'w') as f:
        f.write(resolver_str)
    return cpenv_file


class CpenvShow(Action):

    label = 'Show cpenv'
    identifier = 'cpenv.show'
    description = 'Shows the cpenv modules that will be activated'

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
        return ctx.host == 'cli'

    @classmethod
    def register(cls, cons):
        cons.action_hub.register(cls)
        cons.action_hub.connect(cls.identifier, get_cpenv)
        cons.action_hub.connect(cls.identifier, show_cpenv)

    @classmethod
    def unregister(cls, cons):
        cons.action_hub.disconnect(cls.identifier, show_cpenv)
        cons.action_hub.disconnect(cls.identifier, get_cpenv)
        cons.action_hub.unregister(cls)


@task
@params(kwarg('root'))
@returns(store('cpenv_resolver'))
def get_cpenv(root):
    import cpenv
    return cpenv.resolve(root.path)


@task
@requires(success('get_cpenv'))
@params(store('cpenv_resolver'))
@returns(artifact('cpenv_modules'))
def show_cpenv(resolver):
    import cpenv.cli as cpenv_cli
    modules = sorted(resolver.resolved, key=cpenv_cli._type_and_name)
    return ' '.join([obj.name for obj in modules])


@task
@requires(success('get_cpenv'))
@params(store('cpenv_resolver'))
def activate_cpenv(resolver):
    resolver.activate()


class CpenvList(Action):

    label = 'List cpenv modules'
    identifier = 'cpenv.list'
    description = 'Lists the available cpenv modules'
    parameters = {}

    @staticmethod
    def available(ctx):
        return ctx.host == 'cli'

    @classmethod
    def register(cls, cons):
        cons.action_hub.register(cls)
        cons.action_hub.connect(cls.identifier, list_cpenv_modules)

    @classmethod
    def unregister(cls, cons):
        cons.action_hub.disconnect(cls.identifier, list_cpenv_modules)
        cons.action_hub.unregister(cls)


@task
def list_cpenv_modules():
    import cpenv
    from cpenv.cli import format_objects

    environments = cpenv.get_environments()
    modules = cpenv.get_modules()
    print(format_objects(environments + modules, children=True), end='\n\n')


class CpenvShell(Action):

    label = 'Cpenv Subshell'
    identifier = 'cpenv.shell'
    description = 'Activates a cpenv subshell'

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
        return ctx.host == 'cli'

    @classmethod
    def register(cls, cons):
        cons.action_hub.register(cls)
        cons.action_hub.connect(cls.identifier, get_cpenv)
        cons.action_hub.connect(cls.identifier, launch_cpenv_shell)

    @classmethod
    def unregister(cls, cons):
        cons.action_hub.disconnect(cls.identifier, launch_cpenv_shell)
        cons.action_hub.disconnect(cls.identifier, get_cpenv)
        cons.action_hub.unregister(cls)


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
