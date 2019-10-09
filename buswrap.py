import json

import requests

from bwconfig import test as config


class Response:
    '''Wrapper for api response
     
    '''
    def __init__(self, response_string):
        json_r = json.loads(response_string.text)
        if json_r['code'] != 200:
            raise Exception(f'Method {method} failed with: {json_r["text"]}' +
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
        self.oba.parse_refs(r.references)
        return r

    def _agency(self, id):
        '''agency - get details for a specific agency
        '''
        r = self.oba.get_response('agency', endpoint=id)
        return r


class Route:
    def __init__(self, data=None):
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

    def getStops(self):
        pass

    def getTrips(self):
        pass

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
            self[route['id']] = Route(route)
        return route_json

    def _routes_for_agency(self, id):
        '''routes-for-agency - get a list of all routes for an agency
        '''
        return self.oba.get_response('routes-for-agency', endpoint=id)


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
        return Response(r)

    def parse_refs(self, refs):
        return 0 # rrj side step while playing with classes
        for area in ['agencies', 'routes', 'situations', 'stops', 'trips']:
            for e in refs[area]:
                id = e['id']
                ent = Entity(e)
                getattr(self, area).update({id: ent})

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
            return r['data']['entry']['time']

    def get_routes_by_agency(self, id):
        '''wraps _routes_for_agency
        '''
        r = self._routes_for_agency(id)
        return [(route['shortName'], route['description']) for route in r['data']['list']]

    # stubs
    def _arrival_and_departure_for_stop(self, stop_id):
        '''arrival-and-departure-for-stop - details about a specific
        arrival/departure at a stop
        '''
        return self.get_response('arrival-and-departure-for-stop', endpoint=stop_id)



oba = OBA(config['api_key'], config['base_url'])
print(oba.time(True))
print([agency.name for agency in oba.agencies.values()])
for route in oba.routes.values():
    print(route.id, route.shortName)