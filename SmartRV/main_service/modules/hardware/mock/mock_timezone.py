class zonedetect:
    def __init__(self, location=(35.0715, -82.5216)):
        self.location = location

    def lookup_zone(self, lat, lon):
        return 'America/Chicago'
