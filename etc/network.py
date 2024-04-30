import subprocess
import platform

from typing import Final

from colorama import Fore, Back
import scapy.all as scapy


class Network:
    def __init__(self):
        self.default_ip_range: Final[str] = "192.168.1.1/24"
        self.ssid = self._get_current_ssid()

    def _get_current_ssid(self):
        system = platform.system()
        if system == "Windows":
            try:
                output = subprocess.check_output(["netsh", "wlan", "show", "interfaces"]).decode("utf-8")
                ssid_line = [line.strip() for line in output.split("\n") if "SSID" in line][0]
                ssid = ssid_line.split(": ")[1]
                return ssid
            except subprocess.CalledProcessError:
                return "<UNKNOWN>"
        elif system == "Linux":
            try:
                output = subprocess.check_output(["iwgetid"]).decode("utf-8")
                ssid = output.split('"')[1]
                return ssid
            except subprocess.CalledProcessError:
                return "<UNKNOWN>"
        elif system == "Darwin":
            try:
                output = subprocess.check_output([
                    "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport",
                    "-I"
                ]).decode("utf-8")
                ssid_line = [line for line in output.split("\n") if "SSID:" in line][0]
                ssid = ssid_line.split(": ")[1]
                return ssid
            except subprocess.CalledProcessError:
                return "<UNKNOWN>"
        else:
            return "<UNKNOWN>"

    def _scan_network(self, ip_range: str) -> list[dict[str, str]]:
        arp_request = scapy.ARP(pdst=ip_range)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request
        answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

        results = []

        for element in answered_list:
            result = {"ip": element[1].psrc, "mac": element[1].hwsrc}
            results.append(result)

        return results

    def show_imap(self) -> None:
        print(Fore.RED + Back.WHITE + "TODO")
        devices = self._scan_network(self.default_ip_range)

        print(f"{Fore.GREEN}Found {len(devices)} devices in network {self.ssid}.")
        for device in devices:
            ip = device["ip"]
            mac = device["mac"]
            print(f"{Fore.GREEN}{ip} | {Fore.LIGHTCYAN_EX}{mac}")
