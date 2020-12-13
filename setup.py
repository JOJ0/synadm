from setuptools import setup, find_packages

setup(
    name='synadm',
    version='0.14',
    packages=find_packages(),
    install_requires=[
        'Click>=7.0,<8.0',
        'requests',
        'tabulate',
        'PyYaml',
        'click-option-group',
    ],
    entry_points='''
        [console_scripts]
        synadm=synadm.cli:root
    ''',
)
