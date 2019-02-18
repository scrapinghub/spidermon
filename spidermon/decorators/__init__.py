class DecoratorWithAttributes(object):
    name = None
    attributes = {}

    def __init__(self):
        if not self.name:
            raise AttributeError("No name defined!")
        if not self.attributes:
            raise AttributeError("No attributes defined!")

    def __getattr__(self, name):
        if name not in self.attributes:
            raise AttributeError(
                "Invalid {attribute} '{name}', allowed values: {values}".format(
                    attribute=self.name,
                    name=name,
                    values=", ".join(
                        ["'%s'" % attr for attr in self.attributes.keys()]
                    ),
                )
            )
        else:
            return self.attributes[name]


class OptionsDecorator(object):
    @classmethod
    def set_value(cls, options_class, value_name):
        def value_decorator(value):
            def decorator(fn):
                options_class.add_or_create(fn)
                setattr(fn.options, value_name, value)
                return fn

            return decorator

        return value_decorator

    @classmethod
    def set_fixed_value(cls, options_class, value_name, value):
        def decorator(fn):
            options_class.add_or_create(fn)
            setattr(fn.options, value_name, value)
            return fn

        return decorator
