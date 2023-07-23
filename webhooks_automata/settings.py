from typing import Annotated, Union
from pydantic import BaseModel, Field

from .union_models import all_endpoints, all_actions

# TODO: Some pluggable system to allow other providers in other places

Endpoint = Annotated[Union[*all_endpoints], Field(discriminator="provider")]
Action = Annotated[Union[*all_actions], Field(discriminator="type")]


class Automaton(BaseModel):
    endpoint: Endpoint
    action: Action


class Settings(BaseModel):
    automata: list[Automaton]
