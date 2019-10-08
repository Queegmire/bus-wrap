import json

import requests

from bwconfig import test as config


class Response:
    '''response code- a machine-readable response code with the following semantics:
            200 - Success
            400 - The request could not be understood due to an invalid request parameter or some other error
            401 - The application key is either missing or invalid
            404 - The specified resource was not found
            500 - A service exception or error occurred while processing the request
        data - the response payload
            references see the discussion of references below
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
    def __init__(self, data=None):
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
        self.update(data)
    
    def update(self, data):
        self.__dict__.update(data)


class Agencies:
    def __init__(self, oba):
        self.oba = oba
        agency_json = self._agencies_with_coverage()
        self.last_update = agency_json.currentTime
        self.agency_dict = {}
        agency_refs = agency_json.references['agencies']
        for agency in agency_refs:
            self.agency_dict[agency['id']] = Agency(agency)
        agencies = agency_json.data['list']
        for agency in agencies:
            self.agency_dict[agency['agencyId']].update(agency)

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
        self.update(data)
    
    def update(self, data):
        self.__dict__.update(data)


class Routes:
    def __init__(self, oba, agency=None):
        self.oba = oba
        self.route_dict = {}
        self.routes = {}
        agency_list = list(agency.id) if agency else oba.agencies.agency_dict.keys()
        for agency in agency_list:
            self.addAgency(agency)

    def addAgency(self, agency):
        route_json = self._routes_for_agency(agency)
        for route in route_json.data['list']:
            self.route_dict[route['id']] = Route(route)
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
        for agency in self.agencies.agency_dict.values():
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
print([agency.name for agency in oba.agencies.agency_dict.values()])
for route in oba.routes.route_dict.values():
    print(route.id, route.shortName)