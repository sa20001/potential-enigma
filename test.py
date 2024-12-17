import ctypes
import os
import time

# Constants for Windows Console API
STD_OUTPUT_HANDLE = -11

# COORD structure
class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short),
                ("Y", ctypes.c_short)]

# Get the console handle
kernel32 = ctypes.windll.kernel32
stdout_handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

# Function to set the cursor position
def set_cursor_position(x, y):
    coord = COORD(x, y)
    kernel32.SetConsoleCursorPosition(stdout_handle, coord)

# Clear the console
def clear_console():
    os.system("cls")

# Example of moving the cursor and writing in different lines
def process_output(process_id, output):
    set_cursor_position(0, process_id)  # Move to line based on process_id
    print(f"Process {process_id}: {output}")

clear_console()
# Simulate output for 4 processes
for i in range(4):
    process_output(i, f"Running process {i+1}")
    time.sleep(1)

print("Main code")

for i in range(4):
    process_output(i, f"Testing if it's feeasible")
    time.sleep(1)