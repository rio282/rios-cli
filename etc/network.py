import subprocess
import platform

from typing import Final

from colorama import Fore

import nmap3


class Network:
    def __init__(self):
        self.fail = False
        self.nmap = nmap3.NmapHostDiscovery()

        self.default_gateway: Final[str] = "192.168.1.0"
        self.default_ip_range: Final[str] = f"{self.default_gateway}/24"
        self.ssid = self._get_current_ssid()

    def _get_current_ssid(self):
        system = platform.system()
        try:
            if system == "Windows":
                output = subprocess.check_output(["netsh", "wlan", "show", "interfaces"]).decode("utf-8")
                ssid_line = [line.strip() for line in output.split("\n") if "SSID" in line][0]
                ssid = ssid_line.split(": ")[1]
                return ssid
            elif system == "Linux":
                output = subprocess.check_output(["iwgetid"]).decode("utf-8")
                ssid = output.split('"')[1]
                return ssid
            elif system == "Darwin":
                output = subprocess.check_output([
                    "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport",
                    "-I"
                ]).decode("utf-8")
                ssid_line = [line for line in output.split("\n") if "SSID:" in line][0]
                ssid = ssid_line.split(": ")[1]
                return ssid
            else:
                return "<UNKNOWN>"
        except subprocess.CalledProcessError:
            return "<UNKNOWN>"

    def _scan_network(self) -> list[str]:
        results = []

        results = self.nmap.nmap_arp_discovery(self.default_gateway, args="-sn")

        return results

    def show_imap(self) -> None:
        devices = self._scan_network()

        print(f"{Fore.GREEN}Found {len(devices)} devices in network {self.ssid}.")
        for device in devices:
            print(f"{Fore.GREEN}{device}")
