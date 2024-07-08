import subprocess
import platform

from typing import Final


class NetworkService:
    def __init__(self):
        self.default_gateway: Final[str] = "192.168.1.0"
        self.default_ip_range: Final[str] = f"{self.default_gateway}/24"
        self.ssid = self.get_current_ssid()

    def get_current_ssid(self) -> str:
        """
        Shows what SSID we're currently connected to
        :return: The SSID we're connected to OR "<UNKNOWN>".
        """
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

    def get_ssid_password(self) -> str:
        """
        Shows the password of the connected SSID
        :return: The password of the SSID we're connected to OR "<UNKNOWN>".
        """
        # TODO
        return "<UNKNOWN>"