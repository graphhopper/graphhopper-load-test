import locust
import os

from utils import color

from personas.isochrone import PersonaIsochrone
from personas.matrix import PersonaMatrix
from personas.route import PersonaRoute
from personas.route_invalid import PersonaRouteInvalid
from personas.vrp import PersonaVRP


@locust.events.request_failure.add_listener
def failure_handler(request_type, name, response_time, response_length, exception, **kw):
    if "DEBUG" not in os.environ or os.environ["DEBUG"] != "yes":
        return
    msg = f"Request {name} ({request_type}) failed: {exception}"
    print(color.red(msg), flush=True)
