from dataclasses import dataclass


@dataclass
class UploaderConfig:
    storage_state: str
    proxy_settings: dict
    headless: bool
    auth_username: str
    auth_password: str

    def as_dict(self):
        return vars(self)
