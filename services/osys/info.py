from typing import Dict, Any, Optional

import psutil
from colorama import Fore
from psutil._common import bytes2human

from services import sysinfo


class SysInfo:
    class Hardware:
        @staticmethod
        def get_usage_info():
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "cpu_cores_physical": psutil.cpu_count(logical=False),
                "cpu_cores_logical": psutil.cpu_count(logical=True),
                "cpu_used_percentage": psutil.cpu_percent(interval=1),

                "memory_used_raw": bytes2human(int(mem.used / mem.total)),
                "memory_used_percentage": f"{mem.percent:.1f}",

                "disk_usage": disk
            }

        @staticmethod
        def get_temperature_info() -> Dict[str, Any] or str:
            try:
                temps = psutil.sensors_temperatures()
                if not temps:
                    return "Temperature sensors not available on this system."

                temp_info = {}
                for name, entries in temps.items():
                    temp_info[name] = [{
                        "Current": entry.current,
                        "High": entry.high,
                        "Critical": entry.critical
                    } for entry in entries]

                return temp_info
            except AttributeError:
                return "Temperature monitoring not supported on this platform."

    @property
    def all(self) -> Dict[str, Any]:
        return {
            "hardware": {
                "usage": SysInfo.Hardware.get_usage_info(),
                "temperatures": SysInfo.Hardware.get_temperature_info()
            },
            "operating_system": {

            }
        }


def display_sysinfo() -> None:
    tables = ""

    for section, subdict in self.all.items():
        if not isinstance(section, str) and not isinstance(subdict, dict):
            raise ValueError

    return ""


class InfoDisplayer:
    @staticmethod
    def display_sysload():
        stats = sysinfo.all["usage"]
        align_length = 20

        cpu_usage = f"{stats['cpu_percent']:.1f}%"
        memory_usage = f"{stats['memory_info'].percent:.1f}%"
        disk_usage = f"{stats['disk_usage'].percent:.1f}%"

        memory_used = f"{bytes2human(stats['memory_info'].used)} / {bytes2human(stats['memory_info'].total)}"
        memory_free = f"{bytes2human(stats['memory_info'].free)}"

        disk_used = f"{bytes2human(stats['disk_usage'].used)} / {bytes2human(stats['disk_usage'].total)}"
        disk_free = f"{bytes2human(stats['disk_usage'].free)}"

        print()
        print(
            Fore.WHITE +
            f"{''.ljust(8)} {'CPU'.ljust(align_length)} {'Memory'.ljust(align_length)} {'Disk'.ljust(align_length)}"
        )
        print(
            Fore.WHITE +
            f"{'Usage:'.rjust(8)}{Fore.RESET} {cpu_usage.ljust(align_length)} {memory_usage.ljust(align_length)} {disk_usage.ljust(align_length)}"
        )
        print(
            Fore.WHITE +
            f"{'Used:'.rjust(8)}{Fore.RESET} {''.ljust(align_length)} {memory_used.ljust(align_length)} {disk_used.ljust(align_length)}"
        )
        print(
            Fore.WHITE +
            f"{'Free:'.rjust(8)}{Fore.RESET} {''.ljust(align_length)} {memory_free.ljust(align_length)} {disk_free.ljust(align_length)}"
        )
