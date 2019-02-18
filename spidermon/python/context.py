from __future__ import absolute_import
from spidermon.exceptions import NotConfigured


class Context(dict):
    """
    Stores context for python expressions.

    Also keeps track of not configured components (variables) of the context
    to throw NotConfigured exception in the right time, when test is
    evaluated by interpreter, instead of throwing it in building-context time
    """

    def __init__(self, *args, **kwargs):
        super(Context, self).__init__(*args, **kwargs)
        self._notconfigured = []

    def __getitem__(self, item):
        if item in self._notconfigured:
            raise NotConfigured("{} not available!".format(item))
        return super(Context, self).__getitem__(item)

    def extend_via_attrs(self, obj, attrs):
        """Extend context with names of object attributes and their values"""
        for attr in attrs:
            try:
                super(Context, self).__setitem__(attr, getattr(obj, attr))
            except NotConfigured:
                self._notconfigured.append(attr)
