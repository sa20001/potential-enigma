# import os
# from enum import Enum

# # ANSI color codes
# class Colors(Enum):
#     DEBUG = "\033[34m"      # Blue
#     INFO ="\033[32m"        # Green
#     ERROR = "\033[31m"      # Red
#     WARNING = "\033[33m"    # Yellow
#     # RESET = "\033[0m",      # Reset to default color

# class LogType(Enum):
#     DEBUG = "DEBUG"
#     INFO = "INFO"
#     ERROR = "ERROR"
#     WARNING = "WARNING"

# DEBUG = True  # Set to False for release builds
# parent_pid = 1

# # TODO: create a class, because this is terrible

# def print_function(log_type: LogType, message, pid, color : Colors):
#     if pid == parent_pid:
#         print(f"{color.value}[{log_type.value}]\033[0m - Parent: {message}")
#     else:
#         print(f"{color.value}[{log_type.value}]\033[0m - Child {pid}: {message}")

# def log(log_type: LogType, message: str, pid: int):
#     if log_type == LogType.DEBUG and DEBUG:
#         print_function(LogType.DEBUG, message, pid, Colors.DEBUG)
#     elif log_type == LogType.INFO:
#         print_function(LogType.INFO, message, pid, Colors.INFO)
#     elif log_type == LogType.ERROR:
#         print_function(LogType.ERROR, message, pid, Colors.ERROR)
#     elif log_type == LogType.WARNING:
#         print_function(LogType.WARNING, message, pid, Colors.WARNING)

# def logInit(pid:int):
#     parent_pid = pid

import os
from enum import Enum

# ANSI color codes
class Colors(Enum):
    DEBUG = "\033[34m"      # Blue
    INFO = "\033[32m"       # Green
    ERROR = "\033[31m"      # Red
    WARNING = "\033[33m"    # Yellow
    RESET = "\033[0m"       # Reset to default color

class LogType(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    ERROR = "ERROR"
    WARNING = "WARNING"

DEBUG = False  # Set to False for release builds

class Logger:
    # def __init__(self);
    #     return

    @staticmethod
    def print_function(log_type: LogType, message: str, pid: int, color: Colors):
        # Determine if it's a parent or child process and print the message
        # if pid == self.parent_pid:
        #     print(f"{color.value}[{log_type.value}]{Colors.RESET.value} - Parent: {message}")
        # else:
        #     print(f"{color.value}[{log_type.value}]{Colors.RESET.value} - Child {pid}: {message}")
        print(f"{color.value}[{log_type.value}]{Colors.RESET.value} - Process {pid}: {message}")


    @staticmethod
    def log(log_type: LogType, message: str):
        pid = os.getpid()
        # print(pid)
        # print(parent_pid)
        # Log based on the log_type and the PID
        if log_type == LogType.DEBUG and DEBUG:
            Logger.print_function(log_type, message, pid, Colors.DEBUG)
        elif log_type == LogType.INFO:
            Logger.print_function(log_type, message, pid, Colors.INFO)
        elif log_type == LogType.ERROR:
            Logger.print_function(log_type, message, pid, Colors.ERROR)
        elif log_type == LogType.WARNING:
            Logger.print_function(log_type, message, pid, Colors.WARNING)



# # Usage Example
# logger = Logger(pid=os.getpid())  # Instantiate with the current process PID
# logger.log(LogType.DEBUG, "This is a debug message")  # Log as parent process
# logger.log(LogType.INFO, "This is an info message")   # Log as parent process
# logger.log(LogType.ERROR, "This is an error message")  # Log as parent process
# logger.log(LogType.WARNING, "This is an error message")  # Log as parent process

