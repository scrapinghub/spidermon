from schematics.models import Model
from schematics.types import URLType, StringType, ListType


class QuoteItem(Model):
    quote = StringType(required=True)
    author = StringType(required=True)
    author_url = URLType(required=True)
    tags = ListType(StringType)
