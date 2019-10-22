from buswrap import OBA, config

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
