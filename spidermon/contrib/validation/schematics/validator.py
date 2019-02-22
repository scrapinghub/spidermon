from __future__ import absolute_import
import re

import schematics
from schematics.exceptions import ModelValidationError, ModelConversionError

from spidermon.contrib.validation.validator import Validator
from .translator import SchematicsMessageTranslator
from . import monkeypatches


class SchematicsValidator(Validator):
    default_translator = SchematicsMessageTranslator()
    name = "Schematics"

    def __init__(self, model, translator=None, use_default_translator=True):
        super(SchematicsValidator, self).__init__(
            translator=translator, use_default_translator=use_default_translator
        )
        self._model = model
        self._fields_required = {}
        self._save_required_fields()
        self._data = {}

    def _validate(self, data, strict=False):
        self._set_data(data)
        model = self._get_model_instance(strict=strict)
        try:
            model.validate()
        except ModelValidationError as e:
            self._add_errors(e.messages)
        self._restore_required_fields()

    def _reset(self):
        super(SchematicsValidator, self)._reset()
        self._data = {}

    def _set_data(self, data):
        self._data = dict(data)

    def _get_model_instance(self, strict):
        try:
            return self._model(raw_data=self._data, strict=strict)
        except ModelConversionError as e:
            self._add_errors(e.messages)
            for field_name in e.messages.keys():
                self._set_field_as_not_required(field_name)
                self._data.pop(field_name)
            return self._get_model_instance(strict=strict)

    def _save_required_fields(self):
        for field_name, field in self._model._fields.items():
            self._fields_required[field_name] = field.required

    def _restore_required_fields(self):
        for field_name, required in self._fields_required.items():
            self._model._fields[field_name].required = required

    def _set_field_as_not_required(self, field_name):
        if field_name in self._model._fields:
            self._model._fields[field_name].required = False

    def _add_errors(self, errors):
        if schematics.__version__.startswith("1."):
            for field_name, messages in errors.items():
                if isinstance(messages, dict):
                    transformed_errors = self._get_transformed_child_errors(
                        field_name, messages
                    )
                    self._add_errors(transformed_errors)
                else:
                    self._errors[field_name] += (
                        messages if isinstance(messages, list) else [messages]
                    )
        else:
            from schematics.datastructures import FrozenDict

            for field_name, messages in errors.items():
                if isinstance(messages, (dict, FrozenDict)):
                    transformed_errors = self._get_transformed_child_errors(
                        field_name, messages
                    )
                    self._add_errors(transformed_errors)
                else:
                    messages = self._clean_messages(messages)
                    self._errors[field_name] += messages

    def _get_transformed_child_errors(self, field_name, errors):
        return dict([("%s.%s" % (field_name, k), v) for k, v in errors.items()])

    def _clean_messages(self, messages):
        """
        This is necessary when using Schematics 2.*, because it encapsulates
        the validation error messages in a different way.
        """
        from schematics.exceptions import BaseError, ErrorMessage
        from schematics.datastructures import FrozenList

        if type(messages) not in (list, FrozenList):
            messages = [messages]

        clean_messages = []
        for message in messages:
            if isinstance(message, BaseError):
                message = message.messages

            if isinstance(message, ErrorMessage):
                clean_messages.append(message.summary)
            elif isinstance(message, FrozenList):
                for err in message:
                    # err is an ErrorMessage object
                    clean_messages.append(err.summary)
            else:
                clean_messages.append(message)

        return clean_messages
