import win32api
import win32file
import time
import multiprocessing
import os
import sys


from utils.logger import Logger, LogType
import config
import child_process


def list_dvd_reader_windows():
    dvd_drives = []
    drive_types = {
        2: "Removable",
        3: "Fixed",
        4: "Network",
        5: "CD/DVD",
        6: "RAM Disk",
    }

    drives = win32api.GetLogicalDriveStrings().split("\x00")
    for drive in drives:
        if drive:
            drive_type = win32file.GetDriveType(drive)
            if drive_types.get(drive_type) == "CD/DVD":
                dvd_drives.append(drive)
    return dvd_drives



# Get the current local time
current_time = time.localtime()
# Format the time in a readable way (e.g., hour:minute:second)
formatted_time = time.strftime("%H:%M:%S", current_time).replace(':', '_')
logPath = os.path.normpath(os.path.join(config.log_folder_path, f"failed_{formatted_time}.txt"))
def main():

    dvdReader = list_dvd_reader_windows()
    dvdsCount = len(dvdReader)
    
    if dvdReader:
        Logger.log(LogType.INFO, f"Found {dvdsCount} DVDs:")
        for dvd in dvdReader:
            Logger.log(LogType.INFO, dvd)
    else:
        Logger.log(LogType.INFO, "No DVDs found.")

    if dvdsCount == 0:
        return
    elif dvdsCount != 1:
        Logger.log(LogType.INFO, f"Creating {dvdsCount} processes")
    else:
        Logger.log(LogType.INFO,f"Creating {dvdsCount} process")
    
    # Create the folder if it doesn't exist
    os.makedirs(config.log_folder_path, exist_ok=True)
    # Create failed.txt for monitoring failed copies
    with open(f'{logPath}', 'a') as file:
        # Append a string to the file
        file.write(f'The followings copies failed:\n')
    
    processList = []
    # Creating and starting processes
    count=1
    for index, dvd in enumerate(dvdReader):
        process = multiprocessing.Process(target=child_process, args=(dvd,index, logPath))
        processList.append(process)
        process.start()
        count+=1
           

    try:
        # Joining processes
        for process in processList:
            process.join()
        
        Logger.log(LogType.INFO , "All child processes have finished.")

    except KeyboardInterrupt:
        Logger.log( LogType.WARNING,"Parent process received a keyboard interrupt.")
        Logger.log( LogType.WARNING,"Killing the child processes, it will take some time... please wait")
        # When parent gets KeyboardInterrupt, terminate all children
        for p in processList:
            p.terminate()  # This will terminate the child processes
            p.join()  # Wait for each child to terminate
        Logger.log(LogType.WARNING ,"All child processes have been terminated due to parent interrupt.")

    finally:
        Logger.log(LogType.INFO,"Parent process terminating...")
        # TODO add cleanup tasks

    return 0  # 0 = Success


if __name__ == "__main__":
     code = main()
     print(f"Code execution finished with code: {code}")
     sys.exit(code)
    