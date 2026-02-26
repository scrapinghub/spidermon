from typing import Any

STATS_A = {"item_scraped_count": 150}

STATS_B = {"item_scraped_count": 0}

STATS_EMPTY: dict[str, Any] = {}

STATS_TO_EVALUATE = {
    "downloader/exception_count": 16,
    "downloader/response_count": 63785,
    "finish_reason": "finished",
    "item_scraped_count": 29836,
    "has_errors": True,
    "has_redirections": True,
}
