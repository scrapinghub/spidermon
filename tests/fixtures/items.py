from scrapy import Item, Field

class TreeItem(Item):
    child = Field()

class TestItem(Item):
    url = Field()
    title = Field()

