from bwconfig import test as config
import requests
import json


class Entity:
    def __init__(self, ent_dict):
        self.__dict__.update(ent_dict)


class OBA:
    def __init__(self, key, url):
        self.key = key
        self.url = url
        self.agencies = {}
        self.routes = {}
        self.situations = {}
        self.stops = {}
        self.trips = {}

    def make_url(self, method, endpoint=None):
        if endpoint:
            method = f'{method}/{endpoint}'
        return f'{self.url}{method}.json'

    def get_response(self, method, endpoint=None):
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

    def parse_refs(self, refs):
        for area in ['agencies', 'routes', 'situations', 'stops', 'trips']:
            for e in refs[area]:
                id = e['id']
                ent = Entity(e)
                getattr(self, area).update({id: ent})

    def _agencies_with_coverage(self):
        '''agencies-with-coverage - list all supported agencies along with the
        center of their coverage area
        '''
        r = self.get_response('agencies-with-coverage')
        self.parse_refs(r['data']['references'])
        return r

    def _agency(self, id):
        '''agency - get details for a specific agency
        '''
        r = self.get_response('agency', endpoint=id)
        return r

    def arrival_and_departure_for_stop():
        '''arrival-and-departure-for-stop - details about a specific
        arrival/departure at a stop
        '''
        pass

    def arrivals_and_departures_for_stop():
        '''arrivals-and-departures-for-stop - get current arrivals and
        departures for a stop
        '''
        pass

    def block():
        '''block - get block configuration for a specific block
        '''
        pass

    def _current_time(self):
        '''current-time - retrieve the current system time
        '''
        return self.get_response('current-time')

    def route_ids_for_agency():
        '''route-ids-for-agency - get a list of all route ids for an agency
        '''
        pass

    def route():
        '''route - get details for a specific route
        '''
        pass

    def routes_for_agency():
        '''routes-for-agency - get a list of all routes for an agency
        '''
        pass

    def routes_for_location():
        '''routes-for-location - search for routes near a location, optionally
        by route name
        '''
        pass

    def schedule_for_stop():
        '''schedule-for-stop - get the full schedule for a stop on a particular
        day
        '''
        pass

    def shape():
        '''shape - get details for a specific shape (polyline drawn on a map)
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

    def trip():
        '''trip - get details for a specific trip
        '''
        pass

    def trips_for_location():
        '''trips-for-location - get active trips near a location
        '''
        pass

    def trips_for_route():
        '''trips-for-route - get active trips for a route
        '''
        pass

    def vehicles_for_agency():
        '''vehicles-for-agency - get active vehicles for an agency
        '''
        pass

    def agency(self, id):
        r = self._agency(id)
        return r['data']['entry']['name']

    def get_agencies(self, names=False):
        r = self._agencies_with_coverage()
        ids = [agen['agencyId'] for agen in r['data']['list']]
        if names:
            return [self.agencies[aid].name for aid in ids]
        else:
            return ids

    def time(self, human=False):
        r = self._current_time()
        if human:
            return r['data']['entry']['readableTime']
        else:
            return r['data']['entry']['time']


oba = OBA(config['api_key'], config['base_url'])
print(oba.time(True))
print(oba.get_agencies(True))
print(oba.agency(1))
