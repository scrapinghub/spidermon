.. _mixins:

======
Mixins
======

What's a Mixin in Python?
-------------------------

A mixin is a special kind of multiple inheritance. There are two main situations where mixins are used:

* You want to provide a lot of optional features for a class.
* You want to use one particular feature in a lot of different classes.

That's a little definition, but if you want more info you can see that `StackOverFlow post`_, or this `blog`_

.. _`StackOverFLow post`: https://stackoverflow.com/questions/533631/what-is-a-mixin-and-why-are-they-useful
.. _`blog`: https://easyaspython.com/mixins-for-fun-and-profit-cb9962760556

With Spidermon can use four mixins: `StatsMonitorMixin`_, `ValidationMonitorMixin`_, `SpiderMonitorMixin`_, `JobMonitorMixin`_ mixins

.. _`StatsMonitorMixin`:

StatsMonitorMixin
-----------------

We have an example in the next example: 

.. code-block:: python

    # monitors.py
    # (...other monitors...)

    @monitors.name('Item validation')
    class ItemValidationMonitor(Monitor, StatsMonitorMixin):

        @monitors.name('No item validation errors')
        def test_no_item_validation_errors(self):
            validation_errors = getattr(
                self.stats, 'spidermon/validation/fields/errors', 0
            )
            self.assertEqual(
                validation_errors,
                0,
                msg='Found validation errors in {} fields'.format(
                    validation_errors)
            )


In this example, the `ItemValidationMonitor` have inheritance of `Monitor` class. The `Monitor` class have the data property
and in this data property is an `stats` dict. Then, if we don't want to use the mixin, we can do something like:

.. code-block:: python

    @monitors.name('Item validation')
    class ItemValidationMonitor(Monitor):

        @monitors.name('No item validation errors')
        def test_no_item_validation_errors(self):
            validation_errors = getattr(
                self.data.stats, 'spidermon/validation/fields/errors', 0
            )
            ...
            ...
            ...

So, why use mixin? Mixin is used to provide optional features for a class, for this example, we can use the mixin to create another class with the property `data.stats` but if is not configured, an exception will rise.

.. _`JobMonitorMixin`:

JobMonitorMixin
---------------

This is similar to `StatsMonitorMixin`_. If the object don't have the property `data.job`, it will raise an exception

.. _`SpiderMonitorMixin`:

SpiderMonitorMixin
------------------

This class use `StatsMonitorMixin`_ and `JobMonitorMixin`_ . `SpiderMonitorMixin` add the `crawler`, `spider` and `responses` property for be use like the examples above.

This mixin create an `_response` property that is an object for `ResponsesInfo` class. This class has the stats for the response, you can get the number of all codes for requests, 
informational, successfuls, redirections, bad requests, internal server errors, others and errors.

.. _`ValidationMonitorMixin`:

ValidationMonitorMixin
----------------------

This class use `StatsMonitorMixin`_ and add the `_validation` property. 