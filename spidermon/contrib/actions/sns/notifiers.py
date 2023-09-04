from . import SendSNSNotification


class SendSNSNotificationSpiderStarted(SendSNSNotification):
    def run_action(self):
        subject = "Spider Started"
        attributes = {
            "EventType": {"DataType": "String", "StringValue": "SpiderStarted"},
            "SpiderName": {"DataType": "String", "StringValue": self.data.spider.name},
            "StartTime": {
                "DataType": "String",
                "StringValue": str(self.data.stats.start_time),
            },
        }
        self.send_message(subject, attributes)


class SendSNSNotificationSpiderFinished(SendSNSNotification):
    def run_action(self):
        subject = "Spider Finished"
        attributes = {
            "EventType": {"DataType": "String", "StringValue": "SpiderFinished"},
            "SpiderName": {"DataType": "String", "StringValue": self.data.spider.name},
            "ItemsScraped": {
                "DataType": "Number",
                "StringValue": str(self.data.stats.item_scraped_count),
            },
            "FinishTime": {
                "DataType": "String",
                "StringValue": str(self.data.stats.finish_time),
            },
        }
        self.send_message(subject, attributes)
