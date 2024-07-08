from typing import List, Optional, Tuple

import psutil
import serial.tools.list_ports
from colorama import Fore


class COMService:
    @property
    def connections(self):
        ports = []
        for port, desc, hwid in sorted(serial.tools.list_ports.comports()):
            ports.append(f"{port}: {desc} [{hwid}]")
        return ports


class ProcessManager:
    def __init__(self):
        pass

    def get_processes(self) -> Optional[List[Tuple[int, str]]]:
        """List of all running processes with their PID and name."""
        try:
            running_processes = []

            for process in psutil.process_iter():
                if process.is_running():
                    running_processes.append((process.pid, process.name()))

            running_processes.sort(key=lambda p: p[1])
            return running_processes
        except Exception as e:
            print(f"{Fore.RED}Error listing processes: {e}")

        return None

    def list_processes(self) -> None:
        for process in self.get_processes():
            print(f"{Fore.LIGHTBLACK_EX}{process[0]:<5} {Fore.RESET}{process[1]}")

    def kill_process(self, pid: int) -> bool:
        """Kills a process by its PID."""
        try:
            process = psutil.Process(pid)
            process.kill()
            print(f"{Fore.GREEN}Killed process {process.name()} ({pid})")
            return True
        except psutil.NoSuchProcess:
            print(f"{Fore.RED}No process found with PID {pid}.")
        except psutil.AccessDenied:
            print(f"{Fore.RED}Access denied when trying to kill process with PID {pid}.")
        except Exception as e:
            print(f"{Fore.RED}Error killing process with PID {pid}: {e}")
        return False

    def kill_process_by_name(self, process_name: str) -> bool:
        """Kills all processes matching the given name."""
        killed = False

        try:
            for process in psutil.process_iter():
                if process.name().lower() == process_name.lower():
                    process.kill()
                    print(f"{Fore.GREEN}Killed process {process.name()} ({process.pid})")
                    killed = True
        except psutil.NoSuchProcess:
            print(f"{Fore.RED}No such process: {process_name}.")
        except psutil.AccessDenied:
            print(f"{Fore.RED}Access denied when trying to kill process: {process_name}.")
        except Exception as e:
            print(f"{Fore.RED}Error killing process {process_name}: {e}")

        if not killed:
            print(f"{Fore.RED}Couldn't find process named '{process_name}'.")

        return killed


class StatisticsService:
    @property
    def all(self):
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_info": psutil.virtual_memory(),
            "disk_usage": psutil.disk_usage("/")
        }
