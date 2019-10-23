import re
import time

from buswrap import OBA, config

oba = None

def test_oba_creation():
    global oba
    oba = OBA(config['api_key'], config['base_url'])
    assert oba

def test_time_human():
    time_string = oba.time(True)
    pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}"
    matched = re.match(pattern, time_string).group() == time_string
    assert matched, f'time: {time_string} does not match ISO 8601 pattern'

def test_time_epoch():
    time_int = oba.time(False)
    assert isinstance(time_int, int), f'time: {time_int} not an int'
    print(time.time())
    offset = abs(time_int // 1000 - int(time.time()))
    assert offset < 60, f'time: {offset} over 60 seconds out'

def test_agency_count():
    agency_count = len(oba.agencies)
    assert agency_count == 11

def test_agency_kc():
    kc = oba.agencies['1']
    assert kc.name == "Metro Transit", 'Agency 1 not "Metro Transit"'
