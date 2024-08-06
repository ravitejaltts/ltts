import asyncio
import datetime
import threading
from time import sleep

from common_libs.system.scheduled_function import ScheduledFunction

class ScheduledFunctionManager:
    def __init__(self, instance=0):
        """
        Initializes the TimedFunctionManager class.
        """
        self.instance = instance
        self.functions = []
        self.listLock = threading.Lock()
        self.min_wait_time = float('inf')
        self.run_event = None
        self.loop = None
        self.running = True


    def add_timed_function(self, timed_function):
        """
        Adds a new ScheduledFunction object to the list.

        :param timed_function: An instance of ScheduledFunction to be managed.
        """
        if not isinstance(timed_function, ScheduledFunction):
            print("The provided object is not a ScheduledFunction instance.")
            return
        with self.listLock:
            self.functions.append(timed_function)
        new_wait_time = (timed_function.expiration_time - datetime.datetime.now()).total_seconds()

        if new_wait_time < self.min_wait_time and self.loop is not None:
            self.min_wait_time = new_wait_time
            with self.listLock:
                def set_event_from_thread():
                    if  self.loop._closed is False:
                        asyncio.run_coroutine_threadsafe(self.set_event(self.run_event, self.loop), self.loop)
                        print("\nTask was added to scheduled list waking for new run time!\n")
                    else:
                        print("\n We didn't wake the thres for the new run time!\n")
                threading.Thread(target=set_event_from_thread).start()

        else:
            if self.loop is None:
                print("Loop is none - check_run task has not initialized yet?")
            #else:
            #    print("\nTask was added to scheduled with needing new run time!\n")

    async def min_sleep_coroutine(self):
        # Coroutine code
        await asyncio.sleep(self.min_wait_time)

    async def breakout_event_coroutine(self):
        # Coroutine code needed for 3.11 Python
        await self.run_event.wait()

    async def set_event(self, event, loop):
        """ Coroutine to set the event. """
        if self.run_event is not None:
            self.run_event.set()

    def dump_all_scheduled_functions(self):
        # NEED this to reset on florrplan load
        self.functions = []

    async def check_run(self):
        """
        Iterates through all ScheduledFunction objects and calls their run method.
        Manages the list based on the return values of the run method.
        """
        with self.listLock:
            self.run_event = asyncio.Event()
            self.loop = asyncio.get_running_loop()
        print(f"\ncheck_run schedule Loop initializing {self.instance}\n\n")

        while self.running:
            print(f"\ncheck_run schedule check starting run! Instance {self.instance}\n\n")
            self.min_wait_time = float('inf')
            to_remove = []

            self.run_event.clear()
            try:
                for function in self.functions:
                    result, message = await function.run()
                    if result == 0:
                        to_remove.append(function)
                    elif result == -1:
                        print(f"Error: {message}")
                    else:
                        # print(message)
                        self.min_wait_time = min(self.min_wait_time, result)
            except Exception as err:
                print(f"check_run {err}")

            # print("Waiting for list lock to remove)")
            if to_remove != []:
                with self.listLock:
                    for function in to_remove:
                        self.functions.remove(function)

            # print(f"Scheduler sleeping {self.min_wait_time} or until a task is added!")
            # Code updates for 3.11 compatible
            sleepTask = asyncio.create_task(self.min_sleep_coroutine())
            breakoutTask = asyncio.create_task(self.breakout_event_coroutine())
            # Wait for the event to be set or for self.min_wait_time seconds to pass
            done, pending = await asyncio.wait({breakoutTask, sleepTask}, return_when=asyncio.FIRST_COMPLETED)
            try:
                for task in pending:
                    task.cancel()  # Cancel any remaining tasks  # Be sure this has ended
            except:
                pass  # Don't let this stop the loo it is just a check

if __name__ == '__main__':
    # Simple function to print a string
    async def print_message(message):
        print(message)

    # Example usage
    async def main():
        # Add TimedFunction instances to the manager
        manager = ScheduledFunctionManager()

        asyncio.create_task(manager.check_run())

        manager.add_timed_function(ScheduledFunction(function=print_message,
                    args=("Hello",),
                    wait_seconds=2,
                    oneshot=False
                ))
        manager.add_timed_function(ScheduledFunction(function=print_message,
                    args=("See",),
                    wait_seconds=6,
                    oneshot=False
                ))

        manager.add_timed_function(ScheduledFunction(function=print_message,
                    args=("You",),
                    wait_seconds=3,
                    oneshot=False
                ))

        await asyncio.sleep(400)

    # Run the asyncio main function
    asyncio.run(main())
