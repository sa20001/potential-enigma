import os
from tqdm import tqdm
import hashlib
from customPrint import Logger, LogType

# TODO: create a class

bufferSize = 8*1024*1024

def calculate_file_checksum(file_path, buffer_size=bufferSize):
    """
    Calculate the MD5 checksum of a file.
    :param file_path: Path to the file
    :param buffer_size: Buffer size for reading the file
    :return: MD5 checksum as a hexadecimal string
    """

    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(buffer_size):
            md5.update(chunk)
    return md5.hexdigest()


def calculate_folder_checksum(folder_path, buffer_size=bufferSize):
    """
    Calculate the MD5 checksum of all files in a folder, including subfolders.
    :param folder_path: Path to the folder
    :param buffer_size: Buffer size for reading files
    :return: MD5 checksum of the entire folder as a hexadecimal string
    """
    folder_md5 = hashlib.md5()

    # Traverse the folder recursively
    for root, _, files in os.walk(folder_path):
        for file in sorted(files):  # Sorting files to ensure consistent ordering
            file_path = os.path.join(root, file)
            # Calculate the checksum for each file and update the folder checksum
            file_checksum = calculate_file_checksum(file_path, buffer_size)
            folder_md5.update(file_checksum.encode('utf-8'))

    return folder_md5.hexdigest()

    # Example usage:
    # folder_path = 'path/to/your/folder'
    # folder_checksum = calculate_folder_checksum(folder_path)
    # print(f'Checksum of the folder: {folder_checksum}')


def metadata_checksum(folder_path):
    """
    Calculate a checksum for a folder based on file names and sizes.
    :param folder_path: Path to the folder
    :return: MD5 checksum as a hexadecimal string
    """
    folder_md5 = hashlib.md5()
    
    # Traverse the folder recursively
    for root, _, files in os.walk(folder_path):
        for file in sorted(files):  # Sorting ensures consistent ordering
            file_path = os.path.join(root, file)
            
            # Get the file's size
            try:
                file_size = os.path.getsize(file_path)
                # print(f"File {file_path} has size {file_size}")
            except OSError:
                continue  # Skip inaccessible files
            
            # Update the checksum with the relative path and file size
            relative_path = os.path.relpath(file_path, folder_path)
            folder_md5.update(relative_path.encode('utf-8'))
            folder_md5.update(str(file_size).encode('utf-8'))
    
    return folder_md5.hexdigest()

    # Example usage:
    # folder_path = 'path/to/your/dvd/folder'
    # folder_checksum = calculate_folder_metadata_checksum(folder_path)
    # print(f'Checksum of the folder (based on metadata): {folder_checksum}')

def copy_with_progress(src, dst, index, progress_type='file'):
    """
    Copy a directory or file with a progress bar.

    :param progress_type: 'file' for individual file progress, 'overall' for overall progress
    """

    copyPath = os.path.join(src, os.path.basename(dst))

    if os.path.isfile(src):  # Single file
        copy_file_with_progress(src, dst, progress_type)
    elif os.path.isdir(src):  # Directory
        all_files = []
        total_size = 0
        for root, _, files in os.walk(src):
            for file in files:
                src_file = os.path.join(root, file)
                total_size += os.path.getsize(src_file)
                all_files.append((src_file, os.path.join(dst, os.path.relpath(src_file, src))))

        if progress_type == 'overall':  # Overall progress bar
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Copying DVD: \"{copyPath}\"", position= index) as pbar:
                for src_file, dst_file in all_files:
                    # Ensure the destination folder exists
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)

                    # Copy file with progress
                    copy_file_with_progress(src_file, dst_file, progress_type, pbar)
        else:  # Individual file progress bars
            Logger(LogType.INFO, f"Copying DVD: \"{copyPath}\"")
            for src_file, dst_file in all_files:
                # Ensure the destination folder exists
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)

                # Copy file with progress
                copy_file_with_progress(src_file, dst_file, progress_type)

def copy_file_with_progress(src_file, dst_file, progress_type='file', pbar=None, buffer_size=bufferSize):
    """
    Copy a single file with a progress bar.

    :param progress_type: 'file' for individual file progress, 'overall' for overall progress
    :param pbar: Progress bar for overall progress if progress_type is 'overall'
    """
    total_size = os.path.getsize(src_file)
    with open(src_file, 'rb') as fsrc, open(dst_file, 'wb') as fdst:
        if progress_type == 'overall':
            while True:
                chunk = fsrc.read(buffer_size)
                if not chunk:
                    break
                fdst.write(chunk)
                pbar.update(len(chunk))  # Update overall progress bar
        else:  # Individual file progress bar
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Copying {src_file}") as pbar_file:
                while True:
                    chunk = fsrc.read(buffer_size)
                    if not chunk:
                        break
                    fdst.write(chunk)
                    pbar_file.update(len(chunk))  # Update file-specific progress bar

    # Verify checksum
    Logger.log(LogType.DEBUG, f"Verifying checksum for {src_file}...")
    src_checksum = calculate_file_checksum(src_file)
    dst_checksum = calculate_file_checksum(dst_file)
    if src_checksum != dst_checksum:
        Logger.log(LogType.ERROR, f"\nChecksum mismatch for {src_file} -> {dst_file}")
    else:
        Logger.log(LogType.DEBUG, f"Checksum verified for {src_file}")