from setuptools import setup, find_packages

test_requirements = [
    'pytest>=2.7.0',
    'tox'
]

setup(
    name='spidermon',
    version='1.8.0',
    url='https://github.com/scrapinghub/spidermon',
    author='Scrapinghub',
    author_email='info@scrapinghub.com',
    description=('Spidermon is a framework to build monitors for Scrapy '
                 'spiders.'),
    long_description=('Spidermon is a framework to build monitors for Scrapy '
                      'spiders.'),
    license='BSD',
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
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Scrapy',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: System :: Monitoring',
    ],
)
