import datetime

from spidermon import StatsMonitor, MonitorSuite, monitors
from spidermon import TextMonitorRunner, MonitorRunner
from spidermon import Action, SkipAction


STATS = {
    'downloader/exception_count': 96,
    'downloader/exception_type_count/scrapy.xlib.tx._newclient.ResponseFailed': 4,
    'downloader/exception_type_count/scrapy.xlib.tx._newclient.ResponseNeverReceived': 17,
    'downloader/exception_type_count/twisted.internet.error.ConnectionRefusedError': 75,
    'downloader/request_bytes': 32723279,
    'downloader/request_count': 63795,
    'downloader/request_method_count/GET': 63795,
    'downloader/response_bytes': 2328604452,
    'downloader/response_count': 63699,
    'downloader/response_status_count/200': 29774,
    'downloader/response_status_count/204': 3020,
    'downloader/response_status_count/301': 30764,
    'downloader/response_status_count/303': 4,
    'downloader/response_status_count/499': 5,
    'downloader/response_status_count/502': 24,
    'downloader/response_status_count/503': 105,
    'downloader/response_status_count/504': 3,
    'dupefilter/filtered': 15,
    'finish_reason': 'finished',
    'finish_time': datetime.datetime(2015, 4, 29, 13, 38, 25, 561418),
    'hcf/read/batches': 360,
    'hcf/read/requests': 30022,
    'hola/agent_usage/23.227.160.116': 30022,
    'hola/agents': 1,
    'hola/ips': 3356,
    'hola/ips/XX.any_country': 3356,
    'hola/ips_repeated': 458,
    'hola/tunnel_del': 3020,
    'hscollection/items_sent': 29427,
    'item_export/status/few_fields': 347,
    'item_export/status/few_fields_percent': 1.16544636259824,
    'item_export/status/itemhash_changed': 29774,
    'item_export/status/itemhash_changed_percent': 100.0,
    'item_scraped_count': 29774,
    'kafka/sources_sent': 29774,
    'memusage/max': 269193216,
    'memusage/startup': 55193600,
    'request_depth_max': 1,
    'response_received_count': 32931,
    'scheduler/dequeued': 66817,
    'scheduler/dequeued/disk': 63795,
    'scheduler/dequeued/memory': 3022,
    'scheduler/enqueued': 66817,
    'scheduler/enqueued/disk': 63795,
    'scheduler/enqueued/memory': 3022,
    'start_time': datetime.datetime(2015, 4, 29, 10, 38, 49, 717771)
}


@monitors.order(3)
class SpiderMonitor(StatsMonitor):
    """Spider stats monitor"""

    @monitors.name('Crawl duration')
    @monitors.level.high
    @monitors.order(1)
    def test_crawl_duration(self):
        """Ensures that crawl hasn't take too long."""
        pass

    @monitors.name('Requests vs responses')
    @monitors.order(2)
    def test_crawl_requests_vs_responses(self):
        """Checks that most of the requests have a response."""
        pass

    @monitors.name('Finish reason')
    @monitors.level.high
    @monitors.order(3)
    def test_finish_reason(self):
        """Ensures that the spider has finished correctly."""
        pass

    @monitors.name('Download errors')
    @monitors.order(4)
    def test_download_errors(self):
        """Checks for many download errors."""
        pass

    @monitors.name('Redirections')
    @monitors.level.high
    @monitors.order(5)
    def test_redirections(self):
        """Checks for many redirections."""
        pass


@monitors.order(1)
class HolaMonitor(StatsMonitor):
    """Checks hola proxy stats."""

    @monitors.name('Repeated ips')
    @monitors.level.high
    def test_repeated_ips(self):
        """Checks for repeated ips."""
        pass

    @monitors.name('Single Agent')
    def test_single_agent(self):
        """Ensures that only one agent has been used."""
        pass


@monitors.level.high
@monitors.order(2)
class ItemsMonitor(StatsMonitor):
    """Checks exported items."""

    @monitors.name('Few fields')
    def test_few_fields(self):
        """Ensures that not many fields have missing fields."""
        pass

    @monitors.name('New items')
    @monitors.level.low
    def test_new_items(self):
        """Checks how many extracted items were new ones."""
        pass


class AnAction(Action):
    def run_action(self, result, data):
        #print 'ein....'
        #raise SkipAction, 'jarl...'
        #print data.stats.finish_reason
        #print data.stats['finish_reason']
        pass


class BombAction(Action):
    def run_action(self, result, data):
        pass
        #raise Exception('Boom!')


#@monitors.level.normal
class ExampleSuite(MonitorSuite):
    monitors = [
        ('Spider', SpiderMonitor),
        ('Hola', HolaMonitor),
        ('Items', ItemsMonitor),
    ]
    monitors_finished_actions = [
        AnAction,
    ]
    monitors_passed_actions = [
        #BombAction,
        #AnAction,
    ]
    monitors_failed_actions = [
        #AnAction,
        #AnAction,
        #AnAction,
    ]

    """
    def on_monitors_finished(self, result):
        for monitor_result in result.monitor_results:
            if monitor_result.monitor.level == 'HIGH':
                AnAction().run(result)
                break

    def on_monitors_passed(self, result):
        AnAction().run(result)

    def on_monitors_failed(self, result):
        AnAction().run(result)
    """


suite = ExampleSuite()


runner = MonitorRunner()
runner = TextMonitorRunner(verbosity=2)
result = runner.run(suite, data={'stats': STATS})

#print suite.debug_tree()
#print suite.debug_monitors()
#print suite.options

