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
