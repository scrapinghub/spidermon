from setuptools import setup, find_packages

test_requirements = [
    "pytest>=2.7.0",
    "pytest-cov",
    "pytest-mock",
    "jinja2",
    "lxml",
    "premailer",
    "scrapy",
    "slackclient",
    "twisted>=19.7.0",
]

setup(
    name="spidermon",
    version="1.15.2",
    url="https://github.com/scrapinghub/spidermon",
    author="Zyte",
    author_email="opensource@zyte.com",
    description=("Spidermon is a framework to build monitors for Scrapy spiders."),
    long_description=("Spidermon is a framework to build monitors for Scrapy spiders."),
    license="BSD",
    packages=find_packages(),
    package_data={"spidermon": ["VERSION"]},
    zip_safe=False,
    include_package_data=True,
    install_requires=["jsonschema[format]==3.2.0", "python-slugify", "six>=1.12.2"],
    tests_require=test_requirements,
    extras_require={
        # Specific monitors and tools to support notifications and reports
        "monitoring": [
            "scrapy",
            "Jinja2",
            "slackclient",
            "boto",
            "boto3",
            "premailer",
            "sentry-sdk",
        ],
        # Data validation
        "validation": ["schematics==2.1.0"],
        # Tools to run the tests
        "tests": test_requirements,
        "pep8": ["black"],
        # Tools to build and publish the documentation
        "docs": ["sphinx", "sphinx-rtd-theme", "s3cmd"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Scrapy",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.6",
)
