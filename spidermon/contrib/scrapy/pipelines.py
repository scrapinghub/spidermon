import six
import json
from collections import defaultdict

from scrapy.exceptions import DropItem, NotConfigured
from scrapy.utils.misc import load_object
from scrapy import Field

from spidermon.contrib.validation import SchematicsValidator, JSONSchemaValidator
from schematics.models import Model

from .stats import ValidationStatsManager


DEFAULT_ERRORS_FIELD = '_validation'
DEFAULT_ADD_ERRORS_TO_ITEM = False


class ItemValidationPipeline(object):

    def __init__(self, validators, stats, drop_items_with_errors=False,
                 add_errors_to_items=False, errors_field=None):
        self.drop_items_with_errors = drop_items_with_errors
        self.add_errors_to_items = add_errors_to_items
        self.errors_field = errors_field or DEFAULT_ERRORS_FIELD
        self.validators = []
        self.stats = ValidationStatsManager(stats)
        for validator in validators:
            self._add_validator(validator)

    @classmethod
    def from_crawler(cls, crawler):
        validators = []
        validators += [cls._load_jsonschema_validator(v)
                       for v in crawler.settings.getlist('SPIDERMON_VALIDATION_SCHEMAS')]
        validators += [cls._load_schematics_validator(v)
                       for v in crawler.settings.getlist('SPIDERMON_VALIDATION_MODELS')]
        return cls(
            validators=validators,
            stats=crawler.stats,
            drop_items_with_errors=crawler.settings.getbool('SPIDERMON_VALIDATION_DROP_ITEMS_WITH_ERRORS'),
            add_errors_to_items=crawler.settings.get('SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS'),
            errors_field=crawler.settings.get('SPIDERMON_VALIDATION_ERRORS_FIELD'),
        )

    @classmethod
    def _load_jsonschema_validator(cls, schema):
        if isinstance(schema, six.string_types):
            if schema.endswith('.json'):
                with open(schema, 'r') as f:
                    schema = json.load(f)
            else:
                schema = load_object(schema)
                if isinstance(schema, six.string_types):
                    schema = json.loads(schema)
        if not isinstance(schema, dict):
            raise NotConfigured('Invalid schema, jsonschemas must be defined as:\n'
                                '- an object path to a python dict.\n'
                                '- an object path to a JSON string.\n'
                                '- a path to a JSON file.')
        return JSONSchemaValidator(schema)

    @classmethod
    def _load_schematics_validator(cls, model_path):
        model_class = load_object(model_path)
        if not issubclass(model_class, Model):
            raise NotConfigured('Invalid model, models must subclass schematics.models.Model')
        return SchematicsValidator(model_class)

    def process_item(self, item, _):
        data = dict(item)
        self.stats.add_item()
        self.stats.add_fields(len(data.keys()))
        for validator in self.validators:
            ok, errors = validator.validate(data)
            if not ok:
                for field_name, messages in errors.items():
                    for message in messages:
                        self.stats.add_field_error(field_name, message)
                if self.add_errors_to_items:
                    self._add_errors_to_item(item, errors)
        if self.drop_items_with_errors:
            self.stats.add_dropped_item()
            raise DropItem('Validation failed!')
        else:
            return item

    def _add_validator(self, validator):
        self.validators.append(validator)
        self.stats.add_validator(validator.name)

    def _add_errors_to_item(self, item, errors):
        if not self.errors_field in item.__class__.fields:
            item.__class__.fields[self.errors_field] = Field()
        if not self.errors_field in item._values:
            item[self.errors_field] = defaultdict(list)
        for field_name, messages in errors.items():
            item[self.errors_field][field_name] += messages
