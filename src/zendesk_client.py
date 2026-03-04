import time
from datetime import date, timedelta
from typing import Dict, List, Optional

import requests

from src.config import ZendeskConfig


class ZendeskClient:
    RESULTS_PER_PAGE = 100
    MAX_SEARCH_RESULTS = 1000

    def __init__(self, config: ZendeskConfig):
        self._config = config
        self._session = requests.Session()
        self._session.auth = config.auth
        self._session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

    def _get_with_rate_limit(self, url: str, params: Optional[dict] = None) -> dict:
        response = self._session.get(url, params=params)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            time.sleep(retry_after)
            response = self._session.get(url, params=params)

        response.raise_for_status()
        return response.json()

    def _paginate_search(
        self, query: str, sort_by: str = "created_at", sort_order: str = "asc"
    ) -> list[dict]:
        all_results = []
        params = {
            "query": query,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "per_page": self.RESULTS_PER_PAGE,
        }
        url = f"{self._config.base_url}/search.json"

        while url and len(all_results) < self.MAX_SEARCH_RESULTS:
            data = self._get_with_rate_limit(url, params)
            all_results.extend(data.get("results", []))
            url = data.get("next_page")
            params = None  # next_page URL already contains query params

        return all_results

    def search_tickets(
        self,
        start_date: date,
        end_date: date,
        status: Optional[List[str]] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        group_name: Optional[str] = None,
    ) -> list[dict]:
        query_parts = [
            "type:ticket",
            f"created>={start_date.isoformat()}",
            f"created<={end_date.isoformat()}",
        ]
        if status:
            status_query = " ".join(f"status:{s}" for s in status)
            query_parts.append(status_query)
        if priority:
            query_parts.append(f"priority:{priority}")
        if tags:
            for tag in tags:
                query_parts.append(f"tags:{tag}")
        if group_name:
            query_parts.append(f"group:{group_name}")

        query = " ".join(query_parts)
        return self._paginate_search(query)

    def fetch_tickets_by_date_chunks(
        self,
        start_date: date,
        end_date: date,
        chunk_days: int = 30,
        **filters,
    ) -> list[dict]:
        all_tickets = []
        current_start = start_date

        while current_start <= end_date:
            current_end = min(
                current_start + timedelta(days=chunk_days - 1), end_date
            )
            chunk = self.search_tickets(
                start_date=current_start, end_date=current_end, **filters
            )
            all_tickets.extend(chunk)
            current_start = current_end + timedelta(days=1)

        return all_tickets
