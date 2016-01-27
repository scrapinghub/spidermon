from setuptools import setup, find_packages

__version__ = '0.1.0'

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
