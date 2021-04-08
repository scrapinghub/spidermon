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

.. automodule:: spidermon.contrib.monitors.mixins.job
    :members: JobMonitorMixin

.. automodule:: spidermon.contrib.monitors.mixins.spider
    :members: SpiderMonitorMixin

.. automodule:: spidermon.contrib.monitors.mixins.stats
    :members: StatsMonitorMixin

.. automodule:: spidermon.contrib.monitors.mixins.validation
    :members: ValidationMonitorMixin
