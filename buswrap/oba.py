import json

import requests

from .agency import Agencies
from .route import Routes


class OBA:
    # dunder methods
    def __init__(self, key, url):
        self.key = key
        self.url = url
        self.situations = {}
        self.stops = {}
        self.trips = {}
        self.last_access = None
        self.session = None
        self.agencies = Agencies(self)
        self.routes = Routes(self)
        for agency in self.agencies.values():
            self.routes.addAgency(agency.id)

    #  utility methods
    def make_url(self, method, endpoint=None):
        if endpoint:
            method = f'{method}/{endpoint}'
        return f'{self.url}{method}.json'

    def get_response(self, method, endpoint=None):
        if not self.session:
            self.session = requests.Session()
        query = self.make_url(method, endpoint)
        r = self.session.get(query, params={'key': self.key})
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


class Location:
    def __init__(self, center, span=1000):
        self.latitude, self.longitude = center
        self.span = span
