from typing import TypedDict, Optional
from urllib.parse import urlparse

from decouple import Config


class Proxies(TypedDict):
    http: str | None
    https: str | None


def get_proxies(
        config: Config,
        http_proxy_key: str = None,
        https_proxy_key: str = None,
) -> Proxies:
    proxies = {}

    if http_proxy_key:
        proxies['http'] = config(http_proxy_key, default=None)
    if https_proxy_key:
        proxies['https'] = config(https_proxy_key, default=None)

    return proxies


def proxies_to_proxy_settings(proxies: Proxies) -> Optional[dict]:
    if not proxies:
        return None

    proxy = proxies.get('http') or proxies.get('https')

    if not proxy:
        return None

    parsed = urlparse(proxy)
    username = parsed.username
    password = parsed.password
    server = parsed._replace(
        netloc=f"{parsed.hostname}{f':{parsed.port}' if parsed.port else ''}"
    ).geturl()

    proxy_dict = {'server': server}
    if username:
        proxy_dict['username'] = username
    if password:
        proxy_dict['password'] = password

    return proxy_dict
