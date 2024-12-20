import shutil
import os

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