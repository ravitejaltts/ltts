
import re
from setuptools import setup


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('brucetools/bruce.py').read(),
    re.M
    ).group(1)

setup(
    name='brucetools',
    packages = ["brucetools"],
    version=version,
    description = "Python application bare bones template.",
    install_requires=[
        'requests',
        'importlib-metadata; python_version == "3.8"',
    ],
    entry_points={
          "console_scripts": ['bruce=brucetools.bruce:main']
    }
)

