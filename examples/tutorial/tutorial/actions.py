from spidermon.core.actions import Action


class CloseSpiderAction(Action):
    def run_action(self):
        spider = self.data["spider"]
        spider.logger.info("Closing spider")
        spider.crawler.engine.close_spider(spider, "closed_by_spidermon")
