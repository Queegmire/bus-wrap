from bwconfig import test as config
import requests
import json


class OBA:
    def __init__(self, key, url):
        self.key = key
        self.url = url

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
            raise Exception(f'Method {method} failed with: {json_r["text"]} ({json_r["code"]})')
        if json_r['version'] != 2:
            raise Exception(f'Method {method} should be version 2 is version {json_r["version"]}')
        if json_r['data'].get('limitExceeded', False):
            raise Exception(f'Method {method} rate limit exceeded')
        return json_r


oba = OBA(config['api_key'], config['base_url'])
r = oba.get_response('current-time')
print(r)
