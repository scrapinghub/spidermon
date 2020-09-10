from __future__ import absolute_import
import six
import json
from io import BytesIO
from collections import defaultdict

from scrapy.exceptions import DropItem, NotConfigured
from scrapy.utils.misc import load_object
from scrapy.exporters import JsonLinesItemExporter
from scrapy import Field, Item
from scrapy.utils.python import to_unicode

from spidermon.contrib.validation import SchematicsValidator, JSONSchemaValidator
from spidermon.contrib.validation.jsonschema.tools import get_schema_from
from schematics.models import Model

from .stats import ValidationStatsManager


DEFAULT_ERRORS_FIELD = "_validation"
DEFAULT_ADD_ERRORS_TO_ITEM = False
DEFAULT_DROP_ITEMS_WITH_ERRORS = False


class PassThroughPipeline:
    def process_item(self, item, *args):
        return item


class ItemValidationPipeline(object):
    def __init__(
        self,
        validators,
        stats,
        drop_items_with_errors=DEFAULT_DROP_ITEMS_WITH_ERRORS,
        add_errors_to_items=DEFAULT_ADD_ERRORS_TO_ITEM,
        errors_field=None,
    ):
        self.drop_items_with_errors = drop_items_with_errors
        self.add_errors_to_items = add_errors_to_items or DEFAULT_ADD_ERRORS_TO_ITEM
        self.errors_field = errors_field or DEFAULT_ERRORS_FIELD
        self.validators = validators
        self.stats = ValidationStatsManager(stats)
        for _type, vals in validators.items():
            [self.stats.add_validator(_type, val.name) for val in vals]

    @classmethod
    def from_crawler(cls, crawler):
        spidermon_enabled = crawler.settings.getbool("SPIDERMON_ENABLED")
        if not spidermon_enabled:
            return PassThroughPipeline()

        validators = defaultdict(list)
        allowed_types = (list, tuple, dict)

        def set_validators(loader, schema):
            if type(schema) in (list, tuple):
                schema = {Item: schema}
            for obj, paths in schema.items():
                key = obj.__name__
                paths = paths if type(paths) in (list, tuple) else [paths]
                objects = [loader(v) for v in paths]
                validators[key].extend(objects)

        for loader, name in [
            (cls._load_jsonschema_validator, "SPIDERMON_VALIDATION_SCHEMAS"),
            (cls._load_schematics_validator, "SPIDERMON_VALIDATION_MODELS"),
        ]:
            res = crawler.settings.get(name)
            if not res:
                continue
            if type(res) not in allowed_types:
                raise NotConfigured(
                    "Invalid <{}> type for <{}> settings, dict or list/tuple"
                    "is required".format(type(res), name)
                )
            set_validators(loader, res)

        if not validators:
            raise NotConfigured("No validators were found")

        return cls(
            validators=validators,
            stats=crawler.stats,
            drop_items_with_errors=crawler.settings.getbool(
                "SPIDERMON_VALIDATION_DROP_ITEMS_WITH_ERRORS"
            ),
            add_errors_to_items=crawler.settings.getbool(
                "SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS"
            ),
            errors_field=crawler.settings.get("SPIDERMON_VALIDATION_ERRORS_FIELD"),
        )

    @classmethod
    def _load_jsonschema_validator(cls, schema):
        if isinstance(schema, six.string_types):
            schema = get_schema_from(schema)
        if not isinstance(schema, dict):
            raise NotConfigured(
                "Invalid schema, jsonschemas must be defined as:\n"
                "- a python dict.\n"
                "- an object path to a python dict.\n"
                "- an object path to a JSON string.\n"
                "- a path to a JSON file."
            )
        return JSONSchemaValidator(schema)

    @classmethod
    def _load_schematics_validator(cls, model_path):
        model_class = load_object(model_path)
        if not issubclass(model_class, Model):
            raise NotConfigured(
                "Invalid model, models must subclass schematics.models.Model"
            )
        return SchematicsValidator(model_class)

    def process_item(self, item, _):
        validators = self.find_validators(item)
        if not validators:
            # No validators match this specific item type
            return item

        data = self._convert_item_to_dict(item)
        self.stats.add_item()
        self.stats.add_fields(len(list(data.keys())))
        for validator in validators:
            ok, errors = validator.validate(data)
            if not ok:
                self._add_error_stats(errors)
                if self.add_errors_to_items:
                    self._add_errors_to_item(item, errors)
                if self.drop_items_with_errors:
                    self._drop_item(item, errors)
        return item

    def find_validators(self, item):
        find = lambda x: self.validators.get(x.__name__, [])
        return find(item.__class__) or find(Item)

    def _convert_item_to_dict(self, item):
        serialized_json = BytesIO()
        exporter = JsonLinesItemExporter(serialized_json)
        exporter.export_item(item)
        data = json.loads(to_unicode(serialized_json.getvalue(), exporter.encoding))
        serialized_json.close()
        return data

    def _add_errors_to_item(self, item, errors):
        try:
            if self.errors_field not in item.__class__.fields:
                item.__class__.fields[self.errors_field] = Field()
            if self.errors_field not in item._values:
                item[self.errors_field] = defaultdict(list)
        except AttributeError:
            # The item is just a dict object instead of a Scrapy.Item object
            if self.errors_field not in item:
                item[self.errors_field] = defaultdict(list)
        for field_name, messages in errors.items():
            item[self.errors_field][field_name] += messages

    def _drop_item(self, item, errors):
        """
        This method drops the item after detecting validation errors. Note
        that you could override it to add more details about the item that
        is being dropped or to drop the item only when some specific errors
        are detected.
        """
        self.stats.add_dropped_item()
        raise DropItem("Validation failed!")

    def _add_error_stats(self, errors):
        """
        This method adds validation error stats that can be later used to
        detect alert conditions in the monitors.
        """
        for field_name, messages in errors.items():
            for message in messages:
                self.stats.add_field_error(field_name, message)
        self.stats.add_item_with_errors()
