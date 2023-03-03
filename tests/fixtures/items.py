from scrapy import Item, Field


class TreeItem(Item):
    child = Field()


class TestItem(Item):
    __test__ = False

    url = Field()
    title = Field()
    error_test = Field()
