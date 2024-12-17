# import os
# from tqdm import tqdm

# def copy_with_progress(src, dst):
#     """
#     Copy a directory or file with a progress bar.
#     """
#     if os.path.isfile(src):  # Single file
#         copy_file_with_progress(src, dst)
#     elif os.path.isdir(src):  # Directory
#         for root, _, files in os.walk(src):
#             for file in files:
#                 src_file = os.path.join(root, file)
#                 relative_path = os.path.relpath(src_file, src)
#                 dst_file = os.path.join(dst, relative_path)

#                 # Ensure the destination folder exists
#                 os.makedirs(os.path.dirname(dst_file), exist_ok=True)

#                 # Copy file with progress
#                 copy_file_with_progress(src_file, dst_file)

# def copy_file_with_progress(src_file, dst_file, buffer_size=1024*1024):
#     """
#     Copy a single file with a progress bar.
#     """
#     total_size = os.path.getsize(src_file)
#     with open(src_file, 'rb') as fsrc, open(dst_file, 'wb') as fdst:
#         with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Copying {os.path.basename(src_file)}") as pbar:
#             while True:
#                 chunk = fsrc.read(buffer_size)
#                 if not chunk:
#                     break
#                 fdst.write(chunk)
#                 pbar.update(len(chunk))

import os
from tqdm import tqdm

def copy_with_progress(src, dst, index, progress_type='file'):
    """
    Copy a directory or file with a progress bar.

    :param progress_type: 'file' for individual file progress, 'overall' for overall progress
    """

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
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Copying DVD: \"{os.path.basename(dst)}\"", position= index) as pbar:
                for src_file, dst_file in all_files:
                    # Ensure the destination folder exists
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)

                    # Copy file with progress
                    copy_file_with_progress(src_file, dst_file, progress_type, pbar)
        else:  # Individual file progress bars
            print(f"Copying \"{os.path.basename(dst)}\" DVD")
            for src_file, dst_file in all_files:
                # Ensure the destination folder exists
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)

                # Copy file with progress
                copy_file_with_progress(src_file, dst_file, progress_type)

def copy_file_with_progress(src_file, dst_file, progress_type='file', pbar=None, buffer_size=1024*1024):
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
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Copying {os.path.basename(src_file)}") as pbar_file:
                while True:
                    chunk = fsrc.read(buffer_size)
                    if not chunk:
                        break
                    fdst.write(chunk)
                    pbar_file.update(len(chunk))  # Update file-specific progress bar
