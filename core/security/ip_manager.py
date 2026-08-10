from __future__ import annotations
import ipaddress

class IPManager:
    @staticmethod
    def normalize(ip: str) -> str:
        try:
            return str(ipaddress.ip_address(ip.strip()))
        except ValueError as exc:
            raise ValueError("Invalid IP address.") from exc

    @staticmethod
    def is_valid(ip: str) -> bool:
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    @staticmethod
    def version(ip: str) -> int:
        address = ipaddress.ip_address(ip)
        return address.version

    @staticmethod
    def is_private(ip: str) -> bool:
        return ipaddress.ip_address(ip).is_private

    @staticmethod
    def is_loopback(ip: str) -> bool:
        return ipaddress.ip_address(ip).is_loopback

    @staticmethod
    def is_global(ip: str) -> bool:
        return ipaddress.ip_address(ip).is_global