class Stop():
    '''
    arrival-and-departure-for-stop - details about a specific arrival/departure at a stop
    arrivals-and-departures-for-stop - get current arrivals and departures for a stop
    schedule-for-stop - get the full schedule for a stop on a particular day
    '''
    def __init__(self, data):
        self.id = None
        self.latitude = None
        self.longitude = None
        self.direction = None
        self.name = None
        self.code = None
        self.locationType = None
        self.wheelchair = None
        self.route_ids = []
        self.populate(data)

    def populate(self, data):
        self.__dict__.update(data)

    def _arrival_and_departure_for_stop(self):
        pass

    def _arrivals_and_departures_for_stop(self):
        pass

    def _schedule_for_stop(self):
        pass


class Stops(dict):
    '''
    stop-ids-for-agency - get a list of all stops for an agency
    stop - get details for a specific stop
    stops-for-location - search for stops near a location, optionally by stop code
    '''
    def __init__(self, oba):
        self.oba = oba

    def _stop_ids_for_agency(self, agency_id):
        pass

    def _stop(self, stop_id):
        pass

    def _stops_for_location(self, location):
        pass


