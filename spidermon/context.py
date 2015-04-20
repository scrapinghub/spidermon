from .stats import Stats


class Context(object):
    """
    Object containing the available values for rule checking
    """


def create_context_dict(stats):
    """
    Returns a dict with the Context object values
    """
    return {
        'stats': Stats(stats)
    }


def create_context(stats):
    """
    Returns a Context object with the proper values
    """
    context = Context()
    for k, v in create_context_dict(stats).items():
        setattr(context, k, v)
    return context