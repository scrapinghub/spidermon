from setuptools import setup, find_packages

test_requirements = [
    'pytest>=2.7.0',
    'tox'
]

setup(
    name='spidermon',
    version='1.5.0',
    packages=find_packages(),
    package_data={'spidermon': ['VERSION']},
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'six>=1.9.0',
    ],
    tests_require=test_requirements,
    extras_require={
        # Specific monitors and tools to support notifications and reports
        'monitoring': [
            'scrapy',
            'Jinja2',
            'slackclient',
            'boto',
            'premailer'
        ],
        # Data validation
        'validation': [
            'jsonschema',
            'schematics',
            'python-slugify',
            'strict-rfc3339'
        ],
        # Tools to run the tests
        'tests': test_requirements,
        # Tools to build and publish the documentation
        'docs': [
            'sphinx',
            'sphinx-rtd-theme',
            's3cmd'
        ]
    }
)
