import atexit
import time
from utils.logger import Logger, LogType
import shutil

class CleanupManager:
    def __init__(self):
        self.registry = []

    def register(self, func, *args, **kwargs):
        # Clear previous registrations
        self.registry = [(func, args, kwargs)]
        time.sleep(0.1) # Give time to register the function
        atexit.unregister(self.run_cleanup)  # Unregister any previous `run_cleanup`
        time.sleep(0.1) # Give time to register the function
        atexit.register(self.run_cleanup)  # Register with updated list

    def run_cleanup(self):
        # Run the last registered function
        if self.registry:
            func, args, kwargs = self.registry[-1]  # Get the latest entry
            func(*args, **kwargs)


def cleanup(path: str):
    print("Clean up task")
    # TODO not working always
    if path is not None:
        Logger.log(LogType.INFO, f"Cleanup, deleting incomplete folder: \"{path}\"")
        shutil.rmtree(path)

# # Example usage
# manager = CleanupManager()
# manager.register(cleanup, "New Registration")
