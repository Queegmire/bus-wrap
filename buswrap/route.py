from .stop import Stops, Stop


class Route:
    def __init__(self, oba, data=None):
        self.oba = oba
        self.stops = Stops(self.oba)
        self.id = None
        self.agencyId = None
        self.color = None
        self.description = None
        self.disclaimer = None
        self.lang = None
        self.lat = None
        self.lon = None
        self.latSpan = None
        self.lonSpan = None
        self.longName = None
        self.shortName = None
        self.name = None
        self.timezone = None
        self.phone = None
        self.type = None
        self.textColor = None
        self.url = None
        self.populate(data)
    
    def populate(self, data):
        self.__dict__.update(data)

    def _stops_for_route(self):
        r = self.oba.get_response("stops-for-route", self.id)
        return r

    def getStops(self):
        response = self._stops_for_route()
        for stop in response.data['references']['stops']:
            self.stops[stop['id']] = Stop(stop)
        self.groupings = response.data['entry']['stopGroupings']


class Routes(dict):
    def __init__(self, oba, *, agency=None, auto_load=True):
        self.oba = oba
        self.routes = {}
        if auto_load:
            agency_list = list(agency.id) if agency else oba.agencies.keys()
            for agency in agency_list:
                self.add_routes_from_agency(agency)

    def add_routes_from_agency(self, agency):
        route_json = self._routes_for_agency(agency)
        for route in route_json.data['list']:
            self[route['id']] = Route(self.oba, route)
        return route_json

    def _routes_for_agency(self, id):
        '''routes-for-agency - get a list of all routes for an agency
        '''
        return self.oba.get_response('routes-for-agency', endpoint=id)
