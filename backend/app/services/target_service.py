import ipaddress
import socket
from urllib.parse import urlparse
from ..config import settings

class UnsafeTargetError(ValueError):
    pass

def validate_network_target(target: str) -> None:
    parsed = urlparse(target)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise UnsafeTargetError("Only valid HTTP/HTTPS targets are allowed")
    if parsed.username or parsed.password:
        raise UnsafeTargetError("Target URLs must not contain credentials")
    if settings.allow_private_targets:
        return
    try:
        addresses = {info[4][0] for info in socket.getaddrinfo(parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)}
    except socket.gaierror as exc:
        raise UnsafeTargetError("Target hostname could not be resolved") from exc
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not ip.is_global:
            raise UnsafeTargetError("Private, loopback, link-local, and reserved targets are blocked")
