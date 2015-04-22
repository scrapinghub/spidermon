import json


class SpidermonJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        from .managers import RuleCheckResult, RuleDefinition
        if isinstance(obj, (RuleCheckResult, RuleDefinition)):
            return obj.to_json()
        else:
            return super(SpidermonJSONEncoder, self).default(obj)


class JSONSerializable(object):
    def json(self, indent=None):
        return json.dumps(self, indent=indent, sort_keys=True, cls=SpidermonJSONEncoder)

    def to_json(self):
        raise NotImplementedError
