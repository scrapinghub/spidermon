.. _topics-commands:

=================
Command line tool
=================

Spidermon comes with a basic CLI to help you setup your first monitors.
After Spidermon installation, you should be able to run spidermon commands.
Some of spidermon commands won't run outside Scrapy projects. You can check
which of them in the commands section below.


Using the ``spidermon`` tool
============================

You can start by running the Spidermon with no arguments and it will print
some usage help and the available commands:

.. code-block:: console

  $ spidermon
  Usage: spidermon [OPTIONS] COMMAND [ARGS]...

    Spidermon basic setup.

  Options:
    --help  Show this message and exit.

  Commands:
    setup    Enable Spidermon and setup the monitors from the Scrapy Monitor...
    version  Print Spidermon version.


Available commands
==================

Here you have a list of the available built-in commands with a description and
some usage examples.
You can always get more info about a command by running:

.. code-block:: console

   spidermon <command> --help

And you can see all available commands with::

.. code-block:: console

   spidermon --help

The ``spidermon version`` command works without an active Scrapy project, and is
a Global command.
All the other commands only work inside Scrapy Projects, and are Project-only
commands.

Global commands:

* `version`

Project-only commands:

* `setup`

version
-------

* Syntax: ``spidermon version``
* Requires project: *no*

Prints the Spidermon version.


setup
-----

* Syntax: ``spidermon setup``
* Requires project: *yes*

The `setup` command `enables Spidermon`_ and asks which `built-in monitors`_
should be enabled/configured in your Scrapy project.
Spidermon built-in monitors:

  - Items Count
  - Errors Count
  - Finish Reasons
  - Unwanted HTTP Codes

The command will update your settings.py according to the given configurations.

.. note::
    Note that, if Spidermon is already enabled it will notify you about it:

    .. code-block:: console

        $ spidermon setup
        Spidermon was already configured on this project!
        Proceed to the settings.py file for further configuration.

When succesful it will notify you about the success of enabling Spidermon.

.. code-block:: console

    $ spidermon setup
    Spidermon was enabled succesfully!

After enabling Spidermon, it will ask you which built-in monitors you want to
enable from the installation.

.. code-block:: console

    $ spidermon setup
    Spidermon was enabled succesfully!
    Enable the Item Count monitor? [y/N]: n

    Enable the Error Count Monitor monitor? [y/N]: n

    Enable the Finish Reason monitor? [y/N]: n

    Enable the Unwanted HTTP Code monitor? [y/N]: y

When enabling a monitor, it will ask for its configurations.

.. code-block:: console

    $ spidermon setup
    Spidermon was enabled succesfully!

    Enable the Item Count monitor? [y/N]: y
    What is the fewest amount of items expected?: 10

    Enable the Error Count monitor? [y/N]: y
    What is the greatest amount of errors expected?: 20

    Enable the Finish Reason monitor? [y/N]: y
    Which finish reasons do you want to track? (separated by comma): finished, error

    Enable the Unwanted HTTP Code monitor? [y/N]: n
    Thanks for enabling the Scrapy Suite!

When a monitor is already configured, it will notify that it is already
configured and proceed with the other monitors configuration.

.. code-block:: console

    $ spidermon setup
    Spidermon was enabled succesfully!

    Enable the Item Count monitor? [y/N]: y
    Already exists a configuration for monitor Item Count Monitor
    Proceed to the settings.py file for further configuration.

    Enable the Error Count monitor? [y/N]: ...


In case of a setting that need a list of parameters, you write them separated by comma as in
the example below:

.. code-block:: console

    $ spidermon setup
    Spidermon was enabled succesfully!

    Enable the Item Count monitor? [y/N]: n

    Enable the Error Count monitor? [y/N]: n

    Enable the Finish Reason monitor? [y/N]: n

    Enable the Unwanted HTTP Code monitor? [y/N]: y
    What is the greatest amount of unwanted HTTP codes expected?: 10
    Which unwanted HTTP codes do you want to track? (separated by comma): 403, 404, 501, 504

    Thanks for enabling the Scrapy Monitor Suite!

When setup finishes, it writes the configurations to settings.py


.. _enables spidermon: https://spidermon.readthedocs.io/en/latest/getting-started.html#enabling-spidermon
.. _built-in monitors: https://spidermon.readthedocs.io/en/latest/monitors.html#is-there-a-basic-scrapy-suite-ready-to-use
