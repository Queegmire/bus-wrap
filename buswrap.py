import json

import requests

from bwconfig import test as config


class Response:
    '''The response element carries the following fields:
        version - response version information
        code - a machine-readable response code with the following semantics:
            200 - Success
            400 - The request could not be understood due to an invalid request parameter or some other error
            401 - The application key is either missing or invalid
            404 - The specified resource was not found
            500 - A service exception or error occurred while processing the request
        text - a human-readable version of the response code
        currentTime - current system time on the api server as milliseconds since the unix epoch
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
        agency_json = oba._agencies_with_coverage()
        self.last_update = agency_json.currentTime
        self.agency_dict = {}
        agency_refs = agency_json.references['agencies']
        for agency in agency_refs:
            self.agency_dict[agency['id']] = Agency(agency)
        agencies = agency_json.data['list']
        for agency in agencies:
            self.agency_dict[agency['agencyId']].update(agency)


class Entity:
    def __init__(self, ent_dict):
        self.__dict__.update(ent_dict)


class OBA:
    # dunder methods
    def __init__(self, key, url):
        self.key = key
        self.url = url
        self.agencies = Agencies(self)
        self.routes = {}
        self.situations = {}
        self.stops = {}
        self.trips = {}
        self.last_access = None

    #  utility methods
    def make_url(self, method, endpoint=None):
        if endpoint:
            method = f'{method}/{endpoint}'
        return f'{self.url}{method}.json'

    def get_response_old(self, method, endpoint=None):
        query = self.make_url(method, endpoint)
        r = requests.get(query, {'key': self.key})
        print(f'{query:=^100}')
        json_r = json.loads(r.text)
        if json_r['code'] != 200:
            raise Exception(f'Method {method} failed with: {json_r["text"]}' +
                            f' ({json_r["code"]})')
        if json_r['version'] != 2:
            raise Exception(f'Method {method} should be version 2 is version' +
                            f' {json_r["version"]}')
        if json_r['data'].get('limitExceeded', False):
            raise Exception(f'Method {method} rate limit exceeded')
        return json_r

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
    def _agencies_with_coverage(self):
        '''agencies-with-coverage - list all supported agencies along with the
        center of their coverage area
        '''
        r = self.get_response('agencies-with-coverage')
        self.parse_refs(r.references)
        return r

    def get_agencies(self, names=False):
        ''' wraps _agencies with coverage
        '''
        r = self._agencies_with_coverage()
        ids = [agen['agencyId'] for agen in r.data['list']]
        if names:
            return [self.agencies.agency_dict[aid].name for aid in ids]
        else:
            return ids

    def _agency(self, id):
        '''agency - get details for a specific agency
        '''
        r = self.get_response('agency', endpoint=id)
        return r

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

    def _routes_for_agency(self, id):
        '''routes-for-agency - get a list of all routes for an agency
        '''
        return self.get_response('routes-for-agency', endpoint=id)

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

    def arrivals_and_departures_for_stop():
        '''arrivals-and-departures-for-stop - get current arrivals and
        departures for a stop
        '''
        pass

    def block():
        '''block - get block configuration for a specific block
        '''
        pass

    def route_ids_for_agency():
        '''route-ids-for-agency - get a list of all route ids for an agency
        '''
        pass

    def route():
        '''route - get details for a specific route
        '''
        pass

    def routes_for_location():
        '''routes-for-location - search for routes near a location, optionally
        by route name
        '''
        pass

    def stop_ids_for_agency():
        '''stop-ids-for-agency - get a list of all stops for an agency
        '''
        pass

    def stop():
        '''stop - get details for a specific stop
        '''
        pass

    def stops_for_location():
        '''stops-for-location - search for stops near a location, optionally
        by stop code
        '''
        pass

    def stops_for_route():
        '''stops-for-route - get the set of stops and paths of travel for a
        particular route
        '''
        pass

    def trip_details():
        '''trip-details - get extended details for a specific trip
        '''
        pass

    def trip_for_vehicle():
        '''trip-for-vehicle - get extended trip details for current trip of a
        specific transit vehicle
        '''
        pass


oba = OBA(config['api_key'], config['base_url'])
print(oba.time(True))
print(oba.get_agencies(True))
