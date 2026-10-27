import os
import shutil
import psutil
import time
import gzip
import logging
import argparse
from datetime import datetime


LOG_FILE = "smartcompress.log"


logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s')

def get_disk_free_percent(path):
    usage = psutil.disk_usage(path)
    return usage.free / usage.total * 100

def should_compress(path):
    try:

        return os.path.isfile(path) and not path.endswith('.gz')
    except Exception as e:
        logging.error(f"Error checking file: {path} - {e}")
        return False

def compress_file(path):
    try:
        with open(path, 'rb') as f_in:
            with gzip.open(path + '.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(path)
        logging.info(f"Compressed: {path}")
    except Exception as e:
        logging.error(f"Compression failed for {path}: {e}")

def find_files_to_compress(directory, limit=10):
    all_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)
            if should_compress(full_path):
                last_access = os.path.getatime(full_path)
                size = os.path.getsize(full_path)
                all_files.append((full_path, last_access, size))


    all_files.sort(key=lambda x: (x[1], -x[2]))
    return [file[0] for file in all_files[:limit]]

def monitor_and_compress(watch_dir, disk_path, threshold, interval):
    while True:
        free_percent = get_disk_free_percent(disk_path)
        print(f"Free space: {free_percent:.2f}%")

        if free_percent < threshold:
            logging.warning("Low disk space! Starting compression cycle.")
            files = find_files_to_compress(watch_dir)
            if files:
                for file_path in files:
                    compress_file(file_path)
            else:
                logging.info("No eligible files to compress.")
        time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compress the coldest files in a folder when disk space runs low.")
    parser.add_argument("--watch-dir", required=True,
                        help="folder whose files may be compressed")
    parser.add_argument("--disk", default="/",
                        help="disk to monitor for free space (default: /)")
    parser.add_argument("--threshold", type=float, default=10,
                        help="start compressing below this %% of free space (default: 10)")
    parser.add_argument("--interval", type=int, default=60,
                        help="seconds between checks (default: 60)")
    args = parser.parse_args()

    watch_dir = os.path.expanduser(args.watch_dir)
    if not os.path.isdir(watch_dir):
        parser.error(f"--watch-dir {watch_dir} is not a folder")

    monitor_and_compress(watch_dir, args.disk, args.threshold, args.interval)
