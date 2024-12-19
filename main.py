
import win32api
import win32file
import ctypes
import time
import multiprocessing
import os
import sys
import traceback
import shutil

from customPrint import Logger, LogType
import config
from copyManager import copy_with_progress, metadata_checksum
from cleanupManager import CleanupManager


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



# Create locks
lock1 = multiprocessing.Lock()
lock2 = multiprocessing.Lock()
checksumList = [] # TODO: check if this is shared across processes and check thread safety logic

# TODO: doesn't work for now, they always get 0
commitedSpace = multiprocessing.Value("L", 0) # i=integer singed, L long unsigned


def child_process(dvd, workerIndex):
    pid = os.getpid()
    Logger.log(LogType.DEBUG, f"Child with pid {pid} started")
    Logger.log(LogType.INFO, "Warming up, it will take some time")

    try:
        worker_function(dvd, workerIndex)
        # print(f"Child {pid} is still running")
    except KeyboardInterrupt:
        Logger.log(LogType.INFO, f"Child {multiprocessing.current_process().name} interrupted.")
    finally:
        Logger.log(LogType.INFO, f"Child {multiprocessing.current_process().name} finished.")


def cleanup(path: str):
    print("Clean up task")
    # TODO not working always
    if path is not None:
        Logger.log(LogType.INFO, f"Cleanup, deleting incomplete folder: \"{path}\"")
        shutil.rmtree(path)

def get_free_space(path):
    """
    Get the remaining free disk space for the given path.
    :param path: Path to check (e.g., a directory or drive)
    :return: Free space in bytes
    """
    free = shutil.disk_usage(path)[2] 
    return free

# # Example usage
# path = "D:\\"
# free_space = get_free_space(path)
# print(f"Free space on {path}: {free_space / (1024**3):.2f} GB")

def get_directory_size(directory):
    """
    Calculate the total size of a directory, including all subdirectories and files.
    :param directory: Path to the directory
    :return: Total size in bytes
    """
    total_size = 0
    for dirpath, _, filenames in os.walk(directory):
        for file in filenames:
            file_path = os.path.join(dirpath, file)
            # Skip inaccessible files
            try:
                total_size += os.path.getsize(file_path)
            except OSError:
                pass
    return total_size

# # Example usage
# path = "G:\\"
# directory_size = get_directory_size(path)
# print(f"Total size of {path}: {directory_size / (1024 ** 3):.2f} GB")

def worker_function(dvd, workerIndex):
        # while True:
        #     continue
        aliasDefined = False
        manager = CleanupManager()
        while (True):

            manager.register(cleanup, None) # Unregister the clean up operation, we don't want to delete succesful copies
            
            time.sleep(10) # Sleep for the time required to detect the DVD

            print(commitedSpace.value)

            # Check if the dvd reader is connected to the pc
            dvdReaderConnected = os.path.ismount(dvd)

            if not dvdReaderConnected:
                 print("Connect the dvd reader to the PC")
                 continue

            # Is disc inside?
            discInside = os.path.exists(dvd)
            if not discInside:
                Logger.log(LogType.DEBUG, f"Is disc inside: {discInside}")
                Logger.log(LogType.WARNING, f"Insert a disc\n")
                continue
            Logger.log(LogType.DEBUG, f"DVD is: {dvd}")

            


            if not aliasDefined:
                # Create alias for dvd reader
                error = ctypes.windll.WINMM.mciSendStringW(f"open {dvd} type cdaudio alias drive", None, 0, None)
                aliasDefined = True
                if (error != 0): Logger.log(LogType.ERROR, f"Error {error} creating alias")
         
            
            # # elapsed_time = time.time() - start_time  # Calculate elapsed time
            # # print(f"Has been {elapsed_time} seconds")
            # if not discInside and not openedTray:
            #     # Open dvd tray
            #     # error = ctypes.windll.WINMM.mciSendStringW("set drive door open", None, 0, None)
            #     error = ctypes.windll.WINMM.mciSendStringW(f"open {"E:"} type cdaudio", None, 0, None)
            #     openedTray = True
            #     if (error != 0): debug_print(f"Error {error} opening the DVD tray")

            
            label = win32api.GetVolumeInformation(dvd)[0]
            input_path = os.path.normpath((os.path.join(dvd, label)))
            output_path = os.path.normpath((os.path.join(config.destinationFolder, label)))
            
            # Check the checksum of the DVD
            checksum = metadata_checksum(dvd)
            # Some dvd players autoclose after some time, this avoid to reread them
            if checksum in checksumList:

                if dvd in config.autoCloseTrays:
                    Logger.log(LogType.WARNING, f"File already processed, but dvd reader closed automatically, check the {logPath} and remove the disk.")
                    continue

                Logger.log(LogType.ERROR, f"{input_path} already processed or throwed error, check the {logPath} and remove the disk")
                error = ctypes.windll.WINMM.mciSendStringW("set drive door open", None, 0, None)
                if (error != 0): Logger.log(LogType.ERROR,f"Error {error} opening the DVD tray")
                continue
            Logger.log(LogType.DEBUG, f"{input_path} checksum: {checksum}")



            dvdSize = get_directory_size(dvd)
            freeSpace = get_free_space(config.destinationFolder)

            with commitedSpace.get_lock():  # Lock for thread-safe updates
                Logger.log(LogType.DEBUG, f"Commited space before {commitedSpace.value}")
                print(dvdSize)
                commitedSpace.value += dvdSize
                Logger.log(LogType.DEBUG, f"Commited space after {commitedSpace.value}")


            Logger.log(LogType.DEBUG, f"Commited {commitedSpace.value/ (1024 ** 3):.2f} GB")
            Logger.log(LogType.DEBUG, f"Remaining {freeSpace/ (1024 ** 3):.2f} GB")

            if commitedSpace.value >= freeSpace:
                Logger.log(LogType.ERROR, f"Not enough space to copy {dvd}")
                continue



            Logger.log(LogType.DEBUG, f"Ready to copy DVD \"{dvd}\" with label \"{label}\"")
            index = 1
            temp = output_path
            # This ensures that only one process can execute this part at a time
            with lock1:
                if os.path.isdir(temp):
                    Logger.log(LogType.DEBUG, f"\"{output_path}\" already exist.")

                    # Check if a dir already exists and deal with it if it exists
                    while (True):
                        if not os.path.isdir(temp):
                            Logger.log(LogType.DEBUG,f"New path will be \"{temp}\"")
                            break

                        temp= os.path.join(os.path.dirname(output_path), f"{os.path.basename(output_path)}_{index}")
                        index+=1
                
            
            # Handle exceptions during copy operation since copying might right exception if the disc is damaged
            try:
                manager.register(cleanup, temp) # Register the clean up operation if the script is stopped by user
                copy_with_progress(dvd, temp, workerIndex, "overall")
                Logger.log(LogType.INFO, f"Copy of \"{input_path}\" completed\n")
            except Exception as e:
                # Handle the exception and print the traceback
                if config.DEBUG: traceback.print_exc()  # Prints the traceback to the console
                Logger.log(LogType.ERROR,f"An error occurred during the copy of \"{input_path}\": {e}")
                Logger.log(LogType.INFO,f"The DVD is probably scratched, but you mou might have more luck with another DVD reader")
                Logger.log(LogType.INFO, f"Deleting incomplete copy folder \"{temp}\"\n")
                shutil.rmtree(temp)
                with lock2:
                    # Open the file in append mode ('a')
                    # File is created if it doesn't already exists
                    with open(f'{logPath}', 'a') as file:
                        # Append a string to the file
                        file.write(f'\tFailed {input_path}.\n')

            finally:
                # This code is always executed regardless of errors
                # When copy is completed eject the disk
                Logger.log(LogType.DEBUG, "Ejecting disk")
                checksumList.append(checksum)
                
                with commitedSpace.get_lock():  # Lock for thread-safe updates
                    commitedSpace.value =- dvdSize
                # TODO manage the case when the user ejct the disk manually and then reinsert the disk
                # e.g if disc not present anymore do not add it to checksum list


                error = ctypes.windll.WINMM.mciSendStringW("set drive door open", None, 0, None)
                if (error != 0): Logger.log(LogType.ERROR,f"Error {error} opening the DVD tray")

                          

            # # Close dvd tray
            # error = ctypes.windll.WINMM.mciSendStringW("set drive door closed", None, 0, None)
            # if (error != 0): print(error)


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
        process = multiprocessing.Process(target=child_process, args=(dvd,index))
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
    