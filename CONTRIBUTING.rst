============
Contributing
============

Contributions are always welcome, and they are greatly appreciated! Every little
bit helps, and credit will always be given. You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/scrapinghub/spidermon/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with `Type: Bug`_ is
open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with
`Type: Enhancement`_ is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

Spidermon could always have more documentation, whether as part of the
`official Spidermon`_ docs, in docstrings, or even on the web in blog posts,
articles, and such.

Anything tagged with `Type: Docs`_ indicates some feature of Spidermon we
identified needing more docs and is open to whoever wants to implement it,

Don't be limited to these issues if you believe that other parts need to be
better documented or fixed.

Submit Feedback and Propose New Features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at
https://github.com/scrapinghub/spidermon/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that contributions are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `spidermon` for local development.

#. Fork the `spidermon` repo on GitHub.

#. Clone your fork locally::

    $ git clone git@github.com:your_name_here/spidermon.git

#. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    $ mkvirtualenv spidermon
    $ cd spidermon/

#. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

#. When you're done making changes, check that your changes pass the tests,
   including testing other Python versions with tox::

    $ pip install -r requirements.txt
    $ pip install -r requirements-test.txt
    $ tox

#. Make sure that your code is correctly formatted using `black`_ . No code will
   be merged without this step::

  $ black .

#. If you changed something related to docs, **make sure it compiles properly**::

    $ cd docs
    $ make html

   Now you can go to `spidermon/docs/build` and open `index.html`.

#. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

#. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

#. The pull request should include tests.

#. If the pull request adds functionality, the docs should be updated.

#. Check https://travis-ci.org/scrapinghub/spidermon/pull_requests
   and make sure that the tests pass for all supported Python versions.

#. Follow the core developers' advice which aim to ensure code's consistency
   regardless of variety of approaches used by many contributors.

#. In case you are unable to continue working on a PR, please leave a short
   comment to notify us. We will be pleased to make any changes required to get
   it done.

.. _`Type: Bug`: https://github.com/scrapinghub/spidermon/labels/Type%3A%20Bug
.. _`Type: Enhancement`: https://github.com/scrapinghub/spidermon/labels/Type%3A%20Enhancement
.. _`Type: Docs`: https://github.com/scrapinghub/spidermon/labels/Type%3A%20Docs
.. _`official Spidermon`: http://spidermon.readthedocs.io/
.. _`black`: https://pypi.org/project/black/
