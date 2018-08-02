from setuptools import setup, find_packages

REQUIREMENTS = [
    "six>=1.9.0",
    "Jinja2==2.7.3",
    "slackclient==1.0.0",
    "boto==2.39.0",
    "premailer==2.9.2",
]

TESTS_REQUIRE = [
    "pytest>=2.7.0",
    "Scrapy"
]

VALIDATION_REQUIRE = [
    "jsonschema==2.6.0",
    "schematics==2.0.1",
    "python-slugify==1.0.2",
    "strict-rfc3339==0.6",
]

DOCS_REQUIRE = [
    "sphinx>=1.2.3",
    "sphinx-rtd-theme>=0.1.6",
    "s3cmd>=1.5.2"
]

setup(
    name='spidermon',
    version='1.3.0',
    packages=find_packages(),
    package_data={"spidermon": ["VERSION"]},
    zip_safe=False,
    include_package_data=True,
    install_requires=REQUIREMENTS,
    tests_require=TESTS_REQUIRE + VALIDATION_REQUIRE,
    extras_require={
        "validation": VALIDATION_REQUIRE,
        "docs": DOCS_REQUIRE,
        "tests": TESTS_REQUIRE
    },
)
