Custom Actions
==============

You can define your own custom actions to be executed by your monitor suites. Just
create a class that inherits from `spidermon.core.actions.Action` and implement
the `run_action` method.

.. code-block:: python

    from spidermon.core.actions import Action


    class MyCustomAction(Action):
        def run_action(self):
            # Include here the logic of your action
            ...


Fallback Actions
================

When creating your own custom actions, you can also add a fallback action to run if
an action throws an unhandled exception. To do this, add a fallback attribute to
your custom action.

.. code-block:: python

    from spidermon.core.actions import Action


    class MyFallbackAction(Action):
        def run_action(self):
            # Include here the logic of your action
            # Runs if MyCustomAction().run_action() throws an unhandled exception
            ...


    class MyCustomAction(Action):
        fallback = MyFallbackAction

        def run_action(self):
            # Include here the logic of your action
            ...


You can also add fallbacks to spidermon built-in actions by subclassing them. For
example, send an email if a slack message could not be sent.

.. code-block:: python

    from spidermon.core.actions import Action
    from spidermon.contrib.actions import Slack
    from spidermon.contrib.actions.email.smtp import SendSmtpEmail


    class MyCustomSlackAction(Slack):
        fallback = SendSmtpEmail
