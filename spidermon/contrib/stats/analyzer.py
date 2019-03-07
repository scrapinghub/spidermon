from __future__ import absolute_import
import re


class StatsAnalyzer(object):
    def __init__(self, stats, prefix=None):
        self.stats = stats
        self.prefix = prefix or ""

    def search(self, pattern, include_matches=False):
        pattern = re.compile(self._get_pattern(pattern))
        results = {}
        for key, count in self.stats.items():
            match = pattern.match(key)
            if match:
                if include_matches:
                    results[key] = (
                        count,
                        match.group(1) if len(match.groups()) else "",
                    )
                else:
                    results[key] = count
        return results

    def _get_pattern(self, pattern):
        if self.prefix:
            return "/".join([self.prefix, pattern])
        else:
            return pattern
