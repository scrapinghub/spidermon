class MonitorObject(object):
    def set_data(self, **data):
        self.data = data
        self.init_data(**data)

    def init_data(self, **data):
        if hasattr(self, 'init_child_data'):
            self.init_child_data(**data)


class StatsMonitorObject(MonitorObject):
    def init_data(self, **data):
        super(StatsMonitorObject, self).init_data(**data)
        self.stats = data.get('stats')


class JobMonitorObject(StatsMonitorObject):
    def init_data(self, **data):
        super(JobMonitorObject, self).init_data(**data)
        self.job = data.get('job')