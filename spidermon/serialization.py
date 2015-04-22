import json


class SpidermonJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        from .rules.results import RuleCheckResult
        from .rules.definitions import RuleDefinition
        from .actions.results import ActionRunResult
        from .actions.definitions import ActionDefinition
        from .monitors import MonitorResult
        serializable_classes = (
            RuleCheckResult,
            RuleDefinition,
            ActionRunResult,
            ActionDefinition,
            MonitorResult,
        )
        if isinstance(obj, serializable_classes):
            return obj.as_dict()
        else:
            return super(SpidermonJSONEncoder, self).default(obj)


class JSONSerializable(object):
    def json(self, indent=4):
        return json.dumps(self, indent=indent, sort_keys=True, cls=SpidermonJSONEncoder)

    def as_dict(self):
        raise NotImplementedError
