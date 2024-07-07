import serial.tools.list_ports


class COMService:
    @property
    def connected(self):
        ports = []
        for port, desc, hwid in sorted(serial.tools.list_ports.comports()):
            ports.append(f"{port}: {desc} [{hwid}]")
        return ports
