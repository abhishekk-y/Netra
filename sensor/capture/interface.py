import psutil
import socket
from typing import List, Dict, Any

class NetworkInterface:
    @staticmethod
    def list_interfaces() -> List[str]:
        return list(psutil.net_if_addrs().keys())

    @staticmethod
    def get_info(interface: str) -> Dict[str, Any]:
        addrs = psutil.net_if_addrs().get(interface, [])
        stats = psutil.net_if_stats().get(interface, None)
        
        info = {
            "name": interface,
            "ip": None,
            "mac": None,
            "mtu": stats.mtu if stats else None,
            "is_up": stats.isup if stats else False,
            "speed": stats.speed if stats else None
        }
        
        for addr in addrs:
            if addr.family == socket.AF_INET:
                info["ip"] = addr.address
            elif addr.family == psutil.AF_LINK:
                info["mac"] = addr.address
                
        return info

    @staticmethod
    def exists(interface: str) -> bool:
        return interface in psutil.net_if_addrs()
