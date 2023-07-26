import abc
import asyncio
from typing import Literal, TYPE_CHECKING, Union
from pydantic import BaseModel, ImportString

if TYPE_CHECKING:
    import starlette.requests

all_actions = list()


class ActionBase(BaseModel, abc.ABC):
    def __init_subclass__(cls, /, **kwargs):
        super().__init_subclass__(**kwargs)
        all_actions.append(cls)
    
    @abc.abstractmethod
    async def perform_action(self, request: "starlette.requests.Request"):
        pass


class CommandsAction(ActionBase):
    type: Literal["commands"]
    commands: list[Union[str, list[str]]]
    env: dict[str, str] = dict()
    stop_on_error: bool = True

    async def perform_action(self, request):
        for cmd in self.commands:
            if isinstance(cmd, str):
                proc = await asyncio.create_subprocess_shell(cmd)
            else:
                proc = await asyncio.create_subprocess_exec(*cmd)
            
            if proc.returncode != 0:
                print("Command `%s` returncode was: %d" % (cmd, proc.returncode))
                if self.stop_on_error:
                    return
                else:
                    print("Ignoring error and proceeding")


class ScriptAction(ActionBase):
    type: Literal["script"]

    async def perform_action(self, request):
        pass


class CallableAction(ActionBase):
    type: Literal["callable"]
    callable: ImportString

    async def perform_action(self, request):
        pass
