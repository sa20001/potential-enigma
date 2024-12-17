
import win32api
import win32file
import ctypes
import time
import multiprocessing
import os
import sys

from customPrint import Logger, LogType
from copyManager import copy_with_progress

destinationFolder = "D:/Downloads/Rip"


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



# Create a lock
lock = multiprocessing.Lock()
def child_process(dvd, workerIndex):
    pid = os.getpid()
    Logger.log(LogType.INFO, f"Child with pid {pid} started")
    Logger.log(LogType.INFO, "Warming up, it will take some time")
    try:
        worker_function(dvd, workerIndex)
        # print(f"Child {pid} is still running")
    except KeyboardInterrupt:
        Logger.log(LogType.INFO, f"Child {multiprocessing.current_process().name} interrupted.")
    finally:
        Logger.log(LogType.INFO, f"Child {multiprocessing.current_process().name} finished.")

        

def worker_function(dvd, workerIndex):
        # while True:
        #     continue
        
        while (True):
            
            time.sleep(10)

            # Is disc inside?
            discInside = os.path.exists(dvd)
            Logger.log(LogType.DEBUG, f"DVD is: {dvd}")
            
            if discInside:
                # Create alias for dvd reader
                error = ctypes.windll.WINMM.mciSendStringW(f"open {dvd} type cdaudio alias drive", None, 0, None)
                if (error != 0): Logger.log(LogType.ERROR, f"Error {error} creating alias")
            else:
                Logger.log(LogType.DEBUG, f"Is disc inside {discInside}")
                Logger.log(LogType.WARNING, f"Insert a disc")

            

            # Check if the dvd reader is connected to the pc
            dvdReaderConnected = os.path.ismount(dvd)


            if not dvdReaderConnected:
                 print("Connect the dvd reader to the PC")
                 continue
            
            # # elapsed_time = time.time() - start_time  # Calculate elapsed time
            # # print(f"Has been {elapsed_time} seconds")
            # if not discInside and not openedTray:
            #     # Open dvd tray
            #     # error = ctypes.windll.WINMM.mciSendStringW("set drive door open", None, 0, None)
            #     error = ctypes.windll.WINMM.mciSendStringW(f"open {"E:"} type cdaudio", None, 0, None)
            #     openedTray = True
            #     if (error != 0): debug_print(f"Error {error} opening the DVD tray")

            if (discInside):
                label = win32api.GetVolumeInformation(dvd)[0]
                Logger.log(LogType.DEBUG, f"Ready to copy DVD \"{dvd}\" with label \"{label}\"")
                
                output = os.path.normpath((os.path.join(destinationFolder, label)))
                # print(output)

                index = 1
                temp = output
                # This ensures that only one process can execute this part at a time
                with lock:
                    if os.path.isdir(temp):
                        Logger.log(LogType.DEBUG, f"\"{output}\" already exist.")

                        # Check if a dir already exists and deal with it if it exists
                        while (True):
                            if not os.path.isdir(temp):
                                Logger.log(LogType.DEBUG,f"New path will be \"{temp}\"")
                                break

                            temp= os.path.join(os.path.dirname(output), f"{os.path.basename(output)}_{index}")
                            index+=1
                    
                    # os.mkdir(temp)
                
                # Copy the disc to the folder
                copy_with_progress(dvd, temp, workerIndex, "overall")
            
                # When copy is completed eject the disk
                error = ctypes.windll.WINMM.mciSendStringW("set drive door open", None, 0, None)
                if (error != 0): Logger.log(LogType.ERROR,f"Error {error} opening the DVD tray")
                

            # # Close dvd tray
            # error = ctypes.windll.WINMM.mciSendStringW("set drive door closed", None, 0, None)
            # if (error != 0): print(error)

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
    
    processList = []

    # Creating and starting processes
    count=1
    for index, payload in enumerate(dvdReader):
        process = multiprocessing.Process(target=child_process, args=(payload,index))
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
        # When parent gets KeyboardInterrupt, terminate all children
        for p in processList:
            p.terminate()  # This will terminate the child processes
            p.join()  # Wait for each child to terminate
        Logger.log(LogType.INFO ,"All child processes have been terminated due to parent interrupt.")

    finally:
        Logger.log(LogType.INFO,"Parent process terminating...")
        # TODO add cleanup tasks

    return 0  # 0 = Success


if __name__ == "__main__":
     code = main()
     print(f"Code execution finished with code: {code}")
     sys.exit(code)
    