from os.path import join, dirname
from setuptools import setup, find_packages

# spidermon.__version__ imports doesn't available yet
__version__ = open(join(dirname(__file__), 'spidermon/VERSION')).read().strip()

setup(
    name = 'spidermon',
    version = __version__,
    packages = find_packages(),
    package_data={'spidermon': ['VERSION']},
    zip_safe = False,
    include_package_data = True,
    install_requires=[
        'six==1.9.0',
    ],
    tests_require=[
        'six==1.9.0',
        "pytest>=2.7.0",
    ]
)
