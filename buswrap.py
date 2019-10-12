import json

import requests

from bwconfig import test as config


class Response:
    '''Wrapper for api response
     
    '''
    def __init__(self, response_string, method=None):
        json_r = json.loads(response_string.text)
        if json_r['code'] != 200:
            source = f'Method {method}' if method else 'Call'
            raise Exception(f'{source} failed with: {json_r["text"]}' +
                            f' ({json_r["code"]})')
        self.version = json_r['version']
        self.code = json_r['code']
        self.text = json_r['text']
        self.currentTime = json_r['currentTime']
        self.data = json_r['data']
        self.references = self.data['references']
        self.keys = self.data.keys()


class Agency:
    def __init__(self, data, ):
        self.id = None
        self.name = None
        self.url = None
        self.timezone = None
        self.lang = None
        self.phone = None
        self.disclaimer = None
        self.lat = None
        self.lon = None
        self.latSpan = None
        self.lonSpan = None
        self.populate(data)
    
    def populate(self, data):
        self.__dict__.update(data)

    def getRoutes(self):
        pass

    def getRouteIds(self):
        pass

    def getStopIds(self):
        pass


class Agencies(dict):
    def __init__(self, oba):
        '''Contains list of agencies
        '''
        self.oba = oba
        agencies_json = self._agencies_with_coverage()
        self.last_update = agencies_json.currentTime
        for agency_ref in agencies_json.references['agencies']:
            self[agency_ref['id']] = Agency(agency_ref)
        for agency_data in agencies_json.data['list']:
            self[agency_data['agencyId']].populate(agency_data)

    def _agencies_with_coverage(self):
        '''agencies-with-coverage - list all supported agencies along with the
        center of their coverage area
        '''
        r = self.oba.get_response('agencies-with-coverage')
        return r

    def _agency(self, id):
        '''agency - get details for a specific agency
        '''
        r = self.oba.get_response('agency', endpoint=id)
        return r


class Location:
    def __init__(self, center, span=1000):
        self.latitude, self.longitude = center
        self.span = span


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
    def __init__(self, oba, agency=None):
        self.oba = oba
        self.routes = {}
        agency_list = list(agency.id) if agency else oba.agencies.keys()
        for agency in agency_list:
            self.addAgency(agency)

    def addAgency(self, agency):
        route_json = self._routes_for_agency(agency)
        for route in route_json.data['list']:
            self[route['id']] = Route(self.oba, route)
        return route_json

    def _routes_for_agency(self, id):
        '''routes-for-agency - get a list of all routes for an agency
        '''
        return self.oba.get_response('routes-for-agency', endpoint=id)


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


class OBA:
    # dunder methods
    def __init__(self, key, url):
        self.key = key
        self.url = url
        self.agencies = Agencies(self)
        self.routes = Routes(self)
        for agency in self.agencies.values():
            self.routes.addAgency(agency.id)
        self.situations = {}
        self.stops = {}
        self.trips = {}
        self.last_access = None

    #  utility methods
    def make_url(self, method, endpoint=None):
        if endpoint:
            method = f'{method}/{endpoint}'
        return f'{self.url}{method}.json'

    def get_response(self, method, endpoint=None):
        query = self.make_url(method, endpoint)
        r = requests.get(query, {'key': self.key})
        return Response(r, method)

    # endpoint methods
    def _current_time(self):
        '''current-time - retrieve the current system time
        '''
        return self.get_response('current-time')

    def time(self, human=False):
        ''' wraps _current_time
        '''
        r = self._current_time()
        if human:
            return r.data['entry']['readableTime']
        else:
            return r.data['entry']['time']

    # stubs
    def _arrival_and_departure_for_stop(self, stop_id):
        '''arrival-and-departure-for-stop - details about a specific
        arrival/departure at a stop
        '''
        return self.get_response('arrival-and-departure-for-stop', endpoint=stop_id)


oba = OBA(config['api_key'], config['base_url'])
print('---- list of agencies ----')
print([agency.name for agency in oba.agencies.values()])
routes = oba.routes.values()
'''for route in routes:
    print(route.id, route.shortName)'''
print(f'Number of routes: {len(routes)}')
route_number = "120"
for route in routes:
    if route.shortName == route_number:
        print(f'*> Route {route_number}: id={route.id}')
        route.getStops()
        print(f'Stops on route: {len(route.stops)}')
print(f'Current time: {oba.time(True)}')
