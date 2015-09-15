import os
import sys
import fnmatch
from setuptools import setup, find_packages

DESCRIPTION = "Resource inventory system"
LONG_DESCRIPTION = '''
System to store and query arbitrary data such config, infrastructure inventory .etc.
'''

INSTALL_REQUIRES = [ p.strip() 
    for p in open('requirements.txt').read().split('\n') 
    if p != '' and not p.startswith('#') ]

AUTHOR = "euforia"
AUTHOR_EMAIL = "euforia@gmail.com"

setup(
    name='vindalu',
    version=metrilyx.version,
    url='https://github.com/vindalu',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license='MIT',
    install_requires=INSTALL_REQUIRES,
    packages=find_packages()
)
