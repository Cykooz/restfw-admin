# encoding: utf-8
import os
import sys
from setuptools import setup, find_packages

sys.path.append('.')


HERE = os.path.abspath(os.path.dirname(__file__))


def cli_cmd(app_name, command_name, func_name=None):
    func_name = func_name or command_name
    tpl = '{cmd} = example_app.{app}.commands.{cmd}:{func}.cli'
    return tpl.format(cmd=command_name, app=app_name, func=func_name)


setup(
    name='example_app',
    version='1.0.0',
    description='Example application for restfw_admin',
    long_description='',
    long_description_content_type='text/x-rst',
    keywords='',
    author='Kirill Kuzminykh',
    author_email='cykooz@gmail.com',
    url='https://github.com/Cykooz/restfw_admin',
    package_dir={'': '.'},
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'test': [
            'pytest',
            'mock',
            'asset',
            'WebTest',
            'cykooz.testing',
            'restfw_admin[test]',
        ],
    },
    install_requires=[
        'setuptools',
        'six',
        'restfw>=8.7.3',
        'restfw_admin',
        'wsgicors',
        'pendulum',
        'pyramid_debugtoolbar',
    ],
    entry_points={
        'console_scripts': [
            'run_example_app = example_app.main:main',
        ],
    },
)
