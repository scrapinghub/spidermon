import logging

import json
from scrapy.utils.misc import load_object
import six
from spidermon.utils import web


def get_schema_from(source):
    if web.is_schema_url(source):
        schema = web.get_contents(source)
        try:
            return json.loads(schema)
        except Exception as e:
            logging.exception(
                str(e) + "\nCould not parse schema from '{}'".format(source)
            )
    elif source.endswith(".json"):
        with open(source, "r") as f:
            try:
                return json.load(f)
            except Exception as e:
                logging.exception(
                    str(e) + "\nCould not parse schema in '{}'".format(source)
                )
    else:
        schema = load_object(source)
        if isinstance(schema, six.string_types):
            return json.loads(schema)
        return schema
