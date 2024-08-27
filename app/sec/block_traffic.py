import os
from collections import OrderedDict

from app import filename_from_root
from app.utils import read_json_file, save_json_file, get_now_as_str
from app.utils.errors import TooManyRequests429

_IGNORE_TEXT = [
    "/docs",
    "/redoc",
    "/openapi.json",

    "/health",
    "/oauth/hash",
    "/web/login/",
]
# "/favicon.ico", "/app.css", etc...
for filename in os.listdir(filename_from_root("app/web/static")):
    _IGNORE_TEXT.append(f"/{filename}")

_THRESHOLDS = {
    400: 8,
    401: 8,
    403: 8,
    404: 8,
    501: 8
}

_BLOCKED_CLIENTS_FILENAME = filename_from_root("data/access_list.json")


class IPFiltering:

    def __init__(self, max_entries: int = 5_000):
        self.__max_entries = max_entries
        self.__access_list: dict = {}
        self.__client_thresholds: OrderedDict[str, dict[int, int]] = OrderedDict()
        self._load_access_list()

    def validate(self, client: str, url: str, **kwargs):
        if client in self.get_blocked_clients():
            raise TooManyRequests429(f"Client {client} is blocked.")

        _client = self.__client_thresholds.get(client)
        if _client is None:
            return

        for status_code, value in _client.items():
            if value <= 0:
                self._block_client(client, status_code, url)
                raise TooManyRequests429(f"Client {client} will be blocked due to too many {status_code} requests.")

    def update(self, status_code: int, path: str, client: str, **kwargs):
        if _ignore_request(path):
            return

        if 200 <= status_code <= 309:
            self._reset_client(client)
            return

        if client not in self.__client_thresholds:
            # don't grow above the limit of clients, remove older
            if len(self.__client_thresholds) >= self.__max_entries:
                self.__client_thresholds.popitem(last=False)
            self.__client_thresholds[client] = {**_THRESHOLDS}

        if status_code in self.__client_thresholds[client]:
            self.__client_thresholds[client][status_code] -= 1
        else:
            self.__client_thresholds[client][status_code] = 5

    def _reset_client(self, client: str):
        self.__client_thresholds.pop(client, default=None)

    def _block_client(self, client: str, status_code: int, url: str):
        self.get_blocked_clients()[client] = {
            "status_code": status_code,
            "url": url,
            "when": get_now_as_str(),
        }
        self._save_access_list()

    def _save_access_list(self):
        save_json_file(_BLOCKED_CLIENTS_FILENAME, self.__access_list)

    def _load_access_list(self):
        self.__access_list = read_json_file(_BLOCKED_CLIENTS_FILENAME)

    def get_blocked_clients(self) -> dict:
        return self.__access_list["blocked_clients"]

    def unblock_client(self, client: str):
        if client in self.__access_list["blocked_clients"]:
            del self.__access_list["blocked_clients"][client]
            self._save_access_list()


def _ignore_request(path: str) -> bool:
    return path in _IGNORE_TEXT


ip_filtering = IPFiltering()
