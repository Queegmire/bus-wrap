from buswrap import OBA, config
from rich import inspect, print as rprint

oba = OBA(config['api_key'], config['base_url'])
oba.routes['1_100169'].getStops()
inspect(oba.routes['1_100169'].stops['1_28060'])
