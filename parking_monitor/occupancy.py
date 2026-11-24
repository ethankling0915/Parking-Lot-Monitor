"""Debounced per-zone occupancy. Pure Python so it can be tested without OpenCV."""


class ZoneState:
    def __init__(self, name, debounce_seconds):
        self.name = name
        self.debounce_seconds = debounce_seconds
        self.occupied = False
        self._pending_since = None

    def update(self, timestamp, observed_occupied):
        """Feed one observation.

        Returns "occupied" or "vacant" when a change has held for the debounce
        period, otherwise None.
        """
        if observed_occupied == self.occupied:
            self._pending_since = None
            return None
        if self._pending_since is None:
            self._pending_since = timestamp
            return None
        if timestamp - self._pending_since >= self.debounce_seconds:
            self.occupied = observed_occupied
            self._pending_since = None
            return "occupied" if observed_occupied else "vacant"
        return None
