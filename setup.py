from setuptools import find_packages, setup

setup(
    name="spidermon",
    version="1.21.0",
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
    install_requires=[
        "jsonschema[format]>=4.21.0",
        "python-slugify",
    ],
    extras_require={
        # Specific monitors and tools to support notifications and reports
        "monitoring": [
            "Jinja2",
            "boto",
            "boto3",
            "itemadapter",
            "premailer",
            "requests",
            "scrapinghub",
            "scrapinghub-entrypoint-scrapy",
            "scrapy",
            "sentry_sdk",
            "slack_sdk",
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Scrapy",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.8",
)
