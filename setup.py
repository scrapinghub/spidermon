from setuptools import setup, find_packages
from spidermon import __version__

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
