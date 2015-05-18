import re


class StatsAnalyzer(object):
    def __init__(self, stats, prefix):
        self.stats = stats
        self.prefix = prefix

    def search(self, pattern, include_matches=False):
        pattern = re.compile('/'.join([self.prefix, pattern]))
        results = {}
        for key, count in self.stats.items():
            match = pattern.match(key)
            if match:
                results[key] = count if not include_matches else (count, match.group(1))
        return results
