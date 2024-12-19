import atexit
import time

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

# # Example usage
# manager = CleanupManager()

# def cleanup(resource_name):
#     print(f"Cleaning up: {resource_name}")

# manager.register(cleanup, "New Registration")
