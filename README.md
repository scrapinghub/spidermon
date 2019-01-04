# Spidermon

[![Build Status](https://img.shields.io/travis/scrapinghub/spidermon.svg)](https://travis-ci.org/scrapinghub/spidermon)

## Overview

Spidermon is an extension for Scrapy spiders.
The package provides useful tools for data validation, stats monitoring,
and notification messages. This way you leave the monitoring task to
Spidermon and just check the reports/notifications.

## Data validation
Spidermon can check the output data produced by Scrapy spiders and verify
it against a schema or model that defines the expected structure,
data types, and value restrictions.

The data validation support is provided by two external libraries:
- [jsonschema](https://github.com/Julian/jsonschema)
- [schematics](https://github.com/schematics/schematics)

### Example
This example uses the schematics library.
```python
from schematics.models import Model
from schematics.types import URLType, StringType


class BlogEntryModel(Model):
    url = URLType(required=True)
    title = StringType(required=True, max_length=80)
    user = StringType(required=True, max_length=40)

```

## Stats monitoring
Spidermon allows you to define conditions that should trigger an alert
based on Scrapy stats. For example:
- total of scraped items
- crawl duration
- request/response rate
- download errors
- too many redirections

### Example
```python
from spidermon import Monitor, monitors
from spidermon.contrib.monitors.mixins import StatsMonitorMixin, JobMonitorMixin


@monitors.name('Item count')
class ItemCountMonitor(Monitor, StatsMonitorMixin, JobMonitorMixin):
    @monitors.name('Minimum number of items')
    def test_minimum_number_of_items(self):
        expected = 25
        msg = 'Number of scraped items is less than %d' % expected
        self.assertGreaterEqual(self.item_scraped_count, expected, msg=msg)

    @property
    def item_scraped_count(self):
        return getattr(self.stats, 'item_scraped_count', 0)

```

## Notification messages
Spidermon supports multiple notification methods.
It offers native support for email and Slack notifications,
you just need to update your project's settings.
You can also implement your own notification methods.

### Email integration
```python
SPIDERMON_EMAIL_SENDER = 'from@provider.com'
SPIDERMON_EMAIL_SUBJECT = 'VERY IMPORTANT [{{data.spider.name}}] SOMETHING IS FAILED CODE RED'
SPIDERMON_EMAIL_TO = [
    'you@provider.com',
]
```

#### Amazon SES
You can also use Amazon Simple Email Service.
You just have to append the following keys to your settings.
```python
SPIDERMON_AWS_ACCESS_KEY = 'key'
SPIDERMON_AWS_SECRET_KEY = 'secret'
```

#### Custom templates
This is a default Spidermon template, but you may add a custom template
to your package and configure it in the project's settings as follows:
```python
SPIDERMON_BODY_HTML_TEMPLATE = 'reports/email/monitors/result.jinja'
```

### Slack integration
You need to create a [bot user](https://api.slack.com/bot-users).
```python
SPIDERMON_SLACK_SENDER_TOKEN = '<SLACK_BOT_API_TOKEN>'
SPIDERMON_SLACK_SENDER_NAME = '<SLACK_BOT_NAME>'
SPIDERMON_SLACK_RECIPIENTS = ['@yourself', '@yourteammate']
```

## Getting started
You can refer to [this guide](docs/getting-started.md) to setup a
demo Scrapy project and configure Spidermon validation, monitoring,
and notification features step-by-step.
