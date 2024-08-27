import os
from collections import OrderedDict

from app import filename_from_root
from app.utils import read_json_file, save_json_file
from app.utils.errors import TooManyRequests429

IGNORE_TEXT = [
    "/docs",
    "/redoc",
    "/openapi.json",

    "/health",
    "/oauth/hash",
    "/web/login/",
]
# "/favicon.ico", "/app.css", etc...
for filename in os.listdir(filename_from_root("app/web/static")):
    IGNORE_TEXT.append(f"/{filename}")

THRESHOLDS = {
    400: 10,
    401: 10,
    403: 10,
    404: 10,
    500: 10,
    501: 10
}

BLOCKED_CLIENTS_FILENAME = filename_from_root("data/access_list.json")


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

    def update(self, status_code: int, path: str, client: str, **kwargs):
        if _ignore_request(path):
            return

        if 200 <= status_code <= 309:
            self._reset_client(client)
            return

        if client not in self._client_thresholds:
            # don't grow above the limit of clients, remove older
            if len(self._client_thresholds) >= self._max_entries:
                self._client_thresholds.popitem(last=False)
            self._client_thresholds[client] = {**THRESHOLDS}

        if status_code in self._client_thresholds[client]:
            self._client_thresholds[client][status_code] -= 1
        else:
            self._client_thresholds[client][status_code] = 9

    def _reset_client(self, client: str):
        self._client_thresholds.pop(client, default=None)

    def _block_client(self, client: str):
        self._blocked_clients.add(client)
        self._save_blocked_ips()

    def _save_blocked_ips(self):
        data = {"blocked_ips": list(self._blocked_clients)}
        save_json_file(BLOCKED_CLIENTS_FILENAME, data)

    def _load_blocked_ips(self):
        _blocked_ips = read_json_file(BLOCKED_CLIENTS_FILENAME)
        self._blocked_clients = set(_blocked_ips["blocked_ips"])


def _ignore_request(path: str) -> bool:
    return path in IGNORE_TEXT
