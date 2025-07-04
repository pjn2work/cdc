import os
from typing import List

from pydantic import BaseModel

from app import logit, logging, filename_from_root
from app.utils import read_json_file, save_json_file

CRED_FILENAME = filename_from_root("data/credentials.json")


class Client(BaseModel):
    client_name: str | None = None
    client_secret: str | None = None
    scopes: List[str] = []
    expire_after: float = 1.0

    def to_dict(self) -> dict:
        return {
            "client_name": self.client_name,
            "client_secret": self.client_secret,
            "scopes": self.scopes,
            "expire_after": self.expire_after,
        }


class Credentials:
    salt: str
    app_secret_key: str
    app_clients: dict[str, Client]

    def from_dict(self, data: dict):
        self.salt = data.get("salt", os.getenv("CECC_SALT", "_def#salt"))
        self.app_secret_key = data.get("app_secret_key", os.getenv("CECC_SECRET_KEY", "_def#app_secret_key"))
        self.app_clients = {k: Client(**v) for k, v in data["app_clients"].items()}

    def to_dict(self) -> dict:
        return {
            "salt": self.salt,
            "app_secret_key": self.app_secret_key,
            "app_clients": {k: v.to_dict() for k, v in self.app_clients.items()}
        }


class ManageCredentials:
    def __init__(self):
        self.cred: Credentials = Credentials()
        self._load_credentials()

    def _save_credentials(self):
        save_json_file(CRED_FILENAME, self.cred.to_dict())

    def _load_credentials(self):
        cred_dict = read_json_file(CRED_FILENAME)
        self.cred.from_dict(cred_dict)

    def get_salt(self) -> str:
        return self.cred.salt

    def get_secret_key(self) -> str:
        return self.cred.app_secret_key

    def get_client(self, client_id: str) -> Client | None:
        return self.cred.app_clients.get(client_id)

    def change_client_secret(self, client: Client, client_secret_hashed: str):
        client.client_secret = client_secret_hashed
        self._save_credentials()

    def admin_get_all_clients(self) -> dict[str, Client]:
        return self.cred.to_dict()["app_clients"]

    def admin_remove_client(self, client_id: str):
        if client_id in self.cred.app_clients:
            logit(f"> User Admin - Removing '{client_id}'", level=logging.WARNING)
            self.cred.app_clients.pop(client_id)

            self._save_credentials()

    def admin_update_client(self, client_id: str, new_client_id: str, data: dict):
        if client_id in self.cred.app_clients:

            if client_id != new_client_id:
                logit(f"> User Admin - Renaming '{client_id}' to '{new_client_id}'", level=logging.WARNING)
                self.cred.app_clients[new_client_id] = self.cred.app_clients.pop(client_id)

            _client = self.cred.app_clients[new_client_id]
            if data["client_secret"]:
                logit(f"> User Admin - Reset Password '{new_client_id}'", level=logging.WARNING)
                _client.client_secret = data["client_secret"]

            logit(f"> User Admin - Updating '{new_client_id}'", level=logging.WARNING)
            _client.client_name = data["client_name"]
            _client.scopes = data["scopes"]
            _client.expire_after = data["expire_after"]
        else:
            logit(f"> User Admin - Creating '{new_client_id}'", level=logging.WARNING)
            self.cred.app_clients[new_client_id] = Client(**data)

        self._save_credentials()
