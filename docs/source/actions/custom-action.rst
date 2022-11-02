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
            # (...)


Fallback Actions
==============

When creating your own custom actions, you can also add a fallback action to run if
an action throws an unhandled exception. To do this, add a fallback attribute to
your custom action.

.. code-block:: python

    from spidermon.core.actions import Action

    class MyFallbackAction(Action):
        def run_action(self):
            # Include here the logic of your action
            # Runs if run_action throws an unhandled exception
            # (...)

    class MyCustomAction(Action):
        fallback = MyFallbackAction()
        def run_action(self):
            # Include here the logic of your action
            # (...)


You can also add fallbacks to spidermon built-in actions by subclassing them.

.. code-block:: python

    from spidermon.core.actions import Action
    from spdiermon.contrib.actions import Sentry

    class MyFallbackAction(Action):
        # Runs if MyCustomSentryAction fails
        def run_action(self):
            # Include here the logic of your action
            # (...)

    class MyCustomSentryAction(Sentry):
        fallback = MyFallbackAction()

