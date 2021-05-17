How do I add required fields coverage validation?
=================================================

When you enable :ref:`item-validation:item validation` in your project you can
use *ValidationMonitorMixin* in your monitor, which allows you to perform some extra
checks on your results.

Considering that we have the :ref:`validation schema <quote-item-validation-schema>` from the
:ref:`getting-started:getting started` section of our documentation, where the **author**
field is required, we want to add a new monitor to ensure that no more than 20% of the items
returned have the **author** not filled.

.. note:: The methods that will be presented next only work to check coverage of fields
   that are defined as **required** in your validation schema.

*ValidationMonitorMixin* gives you the *check_missing_required_fields_percent* method,
which receives a list of field names and the maximum percentage allowed not to be
filled. Using that we can create a monitor that enforces our validation rule:

.. code-block:: python

 from spidermon import Monitor
 from spidermon.contrib.monitors.mixins import ValidationMonitorMixin

 class CoverageValidationMonitor(Monitor, ValidationMonitorMixin):

     def test_required_fields_with_minimum_coverage(self):
         allowed_missing_percentage = 0.2
         self.check_missing_required_fields_percent(
            field_names=["author"],
            allowed_percent=allowed_missing_percentage
         )

We also have the option to set an absolute amount of items that we want to allow
not to be filled. This requires us to use the *check_missing_required_fields*
method. The following monitor will fail if more than 10 items returned do not
have the **author** field filled.

.. code-block:: python

 class CoverageValidationMonitor(Monitor, ValidationMonitorMixin):

     def test_required_fields_with_minimum_coverage(self):
         allowed_missing_items = 10
         self.check_missing_required_fields(
            field_names=["author"],
            allowed_count=allowed_missing_items
         )

Multiple fields
---------------

What if we want to validate more than one field? There are two different ways, depending on whether you
want to use the same thresholds for both fields or a different one for each field.

Using the same threshold, we just need to pass a list with the field names to the desired
validation method as follows:

.. code-block:: python

 class CoverageValidationMonitor(Monitor, ValidationMonitorMixin):

     def test_required_fields_with_minimum_coverage(self):
        allowed_missing_percentage = 0.2
        self.check_missing_required_fields_percent(
            field_names=["author", "author_url"],
            allowed_percent=allowed_missing_percentage
        )

However, if you want a different rule for different fields, you need to create a new
monitor for each field:

.. code-block:: python

 class CoverageValidationMonitor(Monitor, ValidationMonitorMixin):

     def test_min_coverage_author_field(self):
         allowed_missing_percentage = 0.2
         self.check_missing_required_fields_percent(
             field_names=["author"],
             allowed_percent=allowed_missing_percentage
         )

     def test_min_coverage_author_url_field(self):
         allowed_missing_items = 10
         self.check_missing_required_fields(
             field_names=["author_url"],
             allowed_count=allowed_missing_items
         )
