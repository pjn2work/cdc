from collections import OrderedDict

from app.utils import read_json_file, save_json_file
from app.utils.errors import TooManyRequests429

IGNORE_TEXT = (
    "/favicon.ico",
    "/app.css",
    "/app_logo.jpg",
    "/green.png",
    "/red.png",
)

THRESHOLDS = {
    400: 10,
    401: 10,
    403: 10,
    404: 10,
    500: 10,
    501: 10
}

BLOCKED_CLIENTS_FILENAME = "../../data/blocked_ips.json"


class IPFiltering:

    def __init__(self, max_entries: int = 5_000):
        self._max_entries = max_entries
        self._blocked_clients: set = set()
        self._client_thresholds: OrderedDict[str, dict[int, int]] = OrderedDict()
        self._load_blocked_ips()

    def validate(self, client: str, **kwargs):
        if client in self._blocked_clients:
            raise TooManyRequests429(f"Client {client} is blocked.")

        _client = self._client_thresholds.get(client)
        if _client is None:
            return

        for status_code, value in _client.items():
            if value <= 0:
                self._block_client(client)
                raise TooManyRequests429(f"Client {client} will be blocked due to too many {status_code} requests.")

    def update(self, status_code: int, url: str, client: str, **kwargs):
        if _ignore_request(url):
            return

        if 200 <= status_code <= 309:
            self._reset_client(client)
            return

        if status_code not in THRESHOLDS:
            THRESHOLDS[status_code] = 10

        if client not in self._client_thresholds:
            # don't grow above the limit of clients, remove older
            if len(self._client_thresholds) >= self._max_entries:
                self._client_thresholds.popitem(last=False)
            self._client_thresholds[client] = {**THRESHOLDS}

        self._client_thresholds[client][status_code] -= 1

    def _reset_client(self, client: str):
        self._client_thresholds.pop(client, default=None)

    def _block_client(self, client: str):
        self._blocked_clients.add(client)
        self._save_blocked_ips()

    def _save_blocked_ips(self):
        data = {"blocked_ips": list(self._blocked_clients)}
        save_json_file(BLOCKED_CLIENTS_FILENAME, data, same_as=__file__)

    def _load_blocked_ips(self):
        _blocked_ips = read_json_file(BLOCKED_CLIENTS_FILENAME, same_as=__file__)
        self._blocked_clients = set(_blocked_ips["blocked_ips"])


def _ignore_request(url: str) -> bool:
    for text in IGNORE_TEXT:
        if text in url:
            return True
    return False
