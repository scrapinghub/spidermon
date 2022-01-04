from spidermon.core.options import ActionOptions
from spidermon.decorators import OptionsDecorator


name = OptionsDecorator.set_value(ActionOptions, "name")
description = OptionsDecorator.set_value(ActionOptions, "description")
