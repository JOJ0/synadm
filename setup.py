from setuptools import setup

setup(
    name='synadm',
    version='0.13',
    py_modules=['synadm'],
    install_requires=[
        'Click>=7.0,<8.0',
        'requests',
        'tabulate',
        'PyYaml',
        'click-option-group',
    ],
    entry_points='''
        [console_scripts]
        synadm=synadm:synadm
    ''',
)
