import getpass
import platform
from datetime import datetime
from typing import Dict, Any

import psutil
from colorama import Fore
from psutil._common import bytes2human
from tabulate import tabulate


class SysInfo:
    class Hardware:
        @staticmethod
        def get_usage_info():
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "cpu_cores_(available)": f"{psutil.cpu_count(logical=False)}/{psutil.cpu_count(logical=True)}",
                "cpu_used_percentage": f"{psutil.cpu_percent(interval=1)}%",
                "memory_used": f"{bytes2human(mem.used)}/{bytes2human(mem.total)} ({mem.percent:.1f}%)",
                "disk_used": f"{bytes2human(mem.used)}/{bytes2human(mem.total)} ({disk.percent:.1f}%)",
                "registered_partitions": " ".join([p.mountpoint for p in psutil.disk_partitions()])
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
                return "Temperature monitoring not supported by this device/platform."

    class OperatingSystem:
        @staticmethod
        def get_uptime() -> str:
            boot_time = psutil.boot_time()
            boot_time_dt = datetime.fromtimestamp(boot_time)
            current_time = datetime.now()
            uptime_duration = current_time - boot_time_dt

            days, remainder = divmod(uptime_duration.total_seconds(), 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)

            return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"

        @staticmethod
        def get_general_info() -> Dict[str, Any]:
            return {
                "operating_system": platform.system(),
                "version": platform.version(),
                "release": platform.release(),
                "machine": platform.machine(),
                "processor": platform.processor()
            }

        @staticmethod
        def get_session_info() -> Dict[str, Any]:
            user_name = getpass.getuser()
            login_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d @ %H:%M:%S")

            return {
                "username": user_name,
                "login_time": login_time,
                "system_uptime": SysInfo.OperatingSystem.get_uptime()
            }

    @property
    def all(self) -> Dict[str, Any]:
        return {
            "hardware": {
                "usage": SysInfo.Hardware.get_usage_info(),
                "temperatures": SysInfo.Hardware.get_temperature_info()
            },
            "operating_system": {
                "general": SysInfo.OperatingSystem.get_general_info(),
                "session": SysInfo.OperatingSystem.get_session_info(),
            }
        }


def display_sysinfo() -> None:
    def key_to_name_formatter(raw_key_name: str) -> str:
        return " ".join(raw_key_name.split("_")).title().strip()

    tables = ""
    for section, subsection in sysinfo.all.items():
        if not isinstance(section, str) or not isinstance(subsection, dict):
            raise ValueError

        # create section
        section_title = key_to_name_formatter(section)
        tables += f"\n{Fore.GREEN}*** {section_title}{Fore.RESET}"

        # loop over items in subsection
        for header, info in subsection.items():
            header = key_to_name_formatter(header)
            tables += f"\n\n{Fore.WHITE}{header}{Fore.RESET}\n"
            if isinstance(info, dict):
                rows = [(key_to_name_formatter(key), value) for key, value in info.items()]
                tables += tabulate(rows, tablefmt="outline")
            elif isinstance(info, str):  # -- means an error has occurred
                tables += f"  + Unavailable, reason: {Fore.RED}{info}{Fore.RESET}\n"
            else:
                raise AttributeError(f"Attribute '{info}' must be of type <dict> or <str>")

        tables += "\n"

    print(tables)


sysinfo = SysInfo()
