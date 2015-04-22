import json


class SpidermonJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        from .managers import RuleCheckResult, RuleDefinition
        from .monitors import MonitorResult
        if isinstance(obj, (RuleCheckResult, RuleDefinition, MonitorResult)):
            return obj.to_json()
        else:
            return super(SpidermonJSONEncoder, self).default(obj)


class JSONSerializable(object):
    def json(self, indent=4):
        return json.dumps(self, indent=indent, sort_keys=True, cls=SpidermonJSONEncoder)

    def to_json(self):
        raise NotImplementedError
