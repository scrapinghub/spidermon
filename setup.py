from setuptools import setup, find_packages

setup(
    name = 'spidermon',
    version = '0.1.2',
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
