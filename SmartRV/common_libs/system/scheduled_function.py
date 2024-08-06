import time
import datetime
from types import FunctionType
from pydantic import BaseModel, validator, root_validator
from typing import Tuple, Union, Callable
from typing import Any, Union, Tuple

class ScheduledFunction(BaseModel):
    function: Callable
    args: Union[Any, Tuple[Any, ...]] = None
    wait_seconds: Union[int, float] = 0
    oneshot: bool = True
    expiration_time: datetime.datetime = None

    class Config:
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def initialize(cls, values):
        """Set initial values before validation."""
        values["expiration_time"] = datetime.datetime.now() + datetime.timedelta(seconds=values.get("wait_seconds", 0))
        return values

    @validator('function')
    def check_function_is_callable(cls, v):
        if not callable(v):
            raise ValueError('The function must be callable')
        return v

    @validator('wait_seconds')
    def check_wait_seconds_is_non_negative(cls, v):
        if v < 0:
            raise ValueError('Wait seconds must be a non-negative number')
        return v

    def set_expiration(self, seconds_from_now):
        """
        Sets the expiration time for the function to run.

        :param seconds_from_now: Number of seconds from now to set the expiration time.
        """
        self.expiration_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds_from_now)

    async def run(self):
        """
        Runs the function if the current time is past the expiration time.

        :return: Tuple containing number of seconds until next run (or 0 if successful) and a message.
        """
        if self.expiration_time is None:
            return -1, "Expiration time is not set."

        time_to_run = (self.expiration_time - datetime.datetime.now()).total_seconds()

        if time_to_run > 0:
            return time_to_run, f"Function is not ready to run. {time_to_run}"

        START = time.time()
        print('[ScheduledFunction] START', self.function, flush=True)
        try:
            await self.function(*self.args)
        except Exception as e:
            msg = f"[ScheduledFunction] An error occurred: {e}\n\n"
            print(msg)
            print('[ScheduledFunction] ERROR: ', time.time() - START, self.function, msg, flush=True)
            return -1, msg

        print('[ScheduledFunction] END: ', time.time() - START, self.function, flush=True)

        if self.oneshot is not True:
            self.set_expiration(self.wait_seconds)
            return self.wait_seconds, f"Function executed successfully, will run again in {self.wait_seconds} seconds. "

        return 0, "Function executed successfully."
