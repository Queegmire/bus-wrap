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
