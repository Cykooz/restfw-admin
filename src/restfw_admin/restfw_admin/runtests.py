# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""


def runtests():
    import sys
    import pytest
    from os import environ
    from os.path import dirname, join

    cfg_path = join(dirname(dirname(__file__)), 'setup.cfg')

    args = sys.argv[1:]
    if not args or args[0].startswith('-'):
        args += ['--pyargs', 'restfw_admin']
    args = ['-c', cfg_path] + args
    environ['IS_TESTING'] = 'True'

    return pytest.main(args)
