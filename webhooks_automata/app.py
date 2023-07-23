from typing import ClassVar, TYPE_CHECKING
import yaml

from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.config import Config

from .settings import Settings, Automaton

if TYPE_CHECKING:
    from .union_models.actions import ActionBase
    from .union_models.endpoints import EndpointBase

config = Config(".env")
settings_path = config("AUTOMATA_SETTINGS", default="wha_settings.yaml")
with open(settings_path) as f:
    settings = Settings(**yaml.load(f, Loader=yaml.Loader))


class ActionDispatcher:
    active_endpoints: ClassVar[list[str]] = list()
    action: "ActionBase"
    endpoint: "EndpointBase"

    def __new__(cls, autom: Automaton):
        cls.active_endpoints.append(autom.endpoint.suffix)
        return super().__new__(cls)

    def __init__(self, autom: Automaton):
        self.action = autom.action
        self.endpoint = autom.endpoint

    async def dispatch(self, request):
        allowed = await self.endpoint.authorize(request)
        if not allowed:
            return JSONResponse({'status': 'unauthorized'}, status_code=401)
        task = BackgroundTask(self.action.perform_action, request)
        return JSONResponse({'status': 'triggered'}, background=task)


def startup():
    print("Current active endpoints:")
    for s in ActionDispatcher.active_endpoints:
        print(f"\t/{s}")

routes = list()
for automata in settings.automata:
    suffix = automata.endpoint.suffix
    routes.append(Route(f"/{suffix}", ActionDispatcher(automata).dispatch, methods=["POST"]))

app = Starlette(routes=routes, on_startup=[startup])
