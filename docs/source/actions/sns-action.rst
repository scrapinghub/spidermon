SNS action
==========

This action allows you to send custom notifications to an AWS `Simple Notification Service (SNS)`_ topic when your monitor suites finish their execution.

To use this action, you need to provide the AWS credentials and the SNS topic ARN in your ``settings.py`` file as follows:

.. code-block:: python

    # settings.py
    SPIDERMON_SNS_TOPIC_ARN = '<SNS_TOPIC_ARN>'
    SPIDERMON_AWS_ACCESS_KEY_ID = '<AWS_ACCESS_KEY>'
    SPIDERMON_AWS_SECRET_ACCESS_KEY = '<AWS_SECRET_KEY>'
    SPIDERMON_AWS_REGION_NAME = '<AWS_REGION_NAME>'  # Default is 'us-east-1'

A notification sent to the SNS topic can be further integrated with other AWS services or third-party applications.

The following settings are the minimum needed to make this action work:

SPIDERMON_SNS_TOPIC_ARN
-----------------------

ARN (Amazon Resource Name) of the SNS topic where the message will be published.

SPIDERMON_AWS_ACCESS_KEY_ID
---------------------------

Your AWS access key ID.

SPIDERMON_AWS_SECRET_ACCESS_KEY
-------------------------------

Your AWS secret access key.

.. warning::

    Be careful when using AWS credentials in Spidermon. Do not publish your AWS access key ID or secret access key in public code repositories.

Other settings available:

SPIDERMON_AWS_REGION_NAME
-------------------------

Default: ``us-east-1``

The AWS region where your SNS topic is located.

.. note::

    Ensure that the AWS user associated with the provided credentials has the necessary permissions to publish messages to the specified SNS topic.

.. _`Simple Notification Service (SNS)`: https://aws.amazon.com/sns/
