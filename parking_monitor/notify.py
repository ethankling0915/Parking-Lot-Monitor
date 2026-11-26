"""Send short text messages to a Meshtastic channel over a USB-connected radio."""
import meshtastic.serial_interface


class MeshNotifier:
    def __init__(self, port, channel_index=0, enabled=True):
        self.port = port
        self.channel_index = channel_index
        self.enabled = enabled
        self.iface = None

    def _connect(self):
        self.iface = meshtastic.serial_interface.SerialInterface(devPath=self.port)

    def send(self, text):
        if not self.enabled:
            print(f"[mesh off] {text}")
            return
        try:
            if self.iface is None:
                self._connect()
            self.iface.sendText(text, channelIndex=self.channel_index)
            print(f"[mesh] sent: {text}")
        except Exception as exc:
            # A failed radio send should never stop the monitor. Drop the
            # connection so the next send tries again.
            print(f"[mesh] send failed: {exc}")
            self.close()

    def close(self):
        if self.iface is not None:
            try:
                self.iface.close()
            except Exception:
                pass
            self.iface = None