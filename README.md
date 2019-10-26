# bus-wrap

An simplified wrapper around the One Bus Away API implemented in python.

## Functionality

### OneBusAway
OBA class to encapsulate top level functionality.
- Stores:
  - Persistent session to API endpoint.
  - Last time endpoint was accessed.
  - List of agencies and routes.
- To Do:
  - Add additional list of references including stops, routes, etc.


### Agencies Object
Agencies class to maintain list of individual Agency objects.
- Stores:
###
## Goals

* Create simple higherlevel calls to the underlying API
* Cache data inteligently to minimize unnecessary calls
* Wrap common OBA elements with python objects
* Expose underlying API
