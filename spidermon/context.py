from .stats import Stats


class Context(object):
    pass


def create_context_dict(stats):
    return {'stats': Stats(stats)}


def create_context(stats):
    context = Context()
    for k, v in create_context_dict(stats).items():
        setattr(context, k, v)
    return context