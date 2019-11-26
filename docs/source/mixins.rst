.. _mixins:

======
Mixins
======

What is a Mixin?
----------------

A mixin is a class that implements one or more features that you can apply to
any class through multiple inheritance. For more information, see `What is a
mixin, and why are they useful?`_

.. _What is a mixin, and why are they useful?: https://stackoverflow.com/q/533631

Spidermon offers the following built-in mixins:

- `JobMonitorMixin`_
- `SpiderMonitorMixin`_
- `StatsMonitorMixin`_
- `ValidationMonitorMixin`_.

Spidermon built-in mixins
-------------------------

.. _`JobMonitorMixin`:

JobMonitorMixin
~~~~~~~~~~~~~~~

`JobMonitorMixin code`_

.. _`JobMonitorMixin code`: https://github.com/scrapinghub/spidermon/blob/master/spidermon/contrib/monitors/mixins/job.py

This is similar to `StatsMonitorMixin`_. If the object don't have the property `data.job`, it will raise an exception

.. _`SpiderMonitorMixin`:

SpiderMonitorMixin
~~~~~~~~~~~~~~~~~~

`SpiderMonitorMixin code`_

.. _`SpiderMonitorMixin code`: https://github.com/scrapinghub/spidermon/blob/master/spidermon/contrib/monitors/mixins/spider.py

This class use `StatsMonitorMixin`_ and `JobMonitorMixin`_ . `SpiderMonitorMixin` add the `crawler`, `spider` and `responses` property for be use like the examples above.

This mixin create an `_response` property that is an object for `ResponsesInfo` class. This class has the stats for the response, you can get the number of all codes for requests,
informational, successfuls, redirections, bad requests, internal server errors, others and errors.

.. _`StatsMonitorMixin`:

StatsMonitorMixin
~~~~~~~~~~~~~~~~~

`StatsMonitorMixin code`_

.. _`StatsMonitorMixin code`: https://github.com/scrapinghub/spidermon/blob/master/spidermon/contrib/monitors/mixins/stats.py


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

.. _`ValidationMonitorMixin`:

ValidationMonitorMixin
~~~~~~~~~~~~~~~~~~~~~~

`ValidationMonitorMixin code`_

.. _`ValidationMonitorMixin code`: https://github.com/scrapinghub/spidermon/blob/master/spidermon/contrib/monitors/mixins/validation.py

This class use `StatsMonitorMixin`_ and add the `_validation` property.
