import os
import shutil
import psutil
import time
import gzip
import logging
import argparse
import sys
from datetime import datetime


# Inside a snap, write the log to the snap's private folder; otherwise to the current folder.
LOG_DIR = os.environ.get("SNAP_USER_COMMON", ".")
LOG_FILE = os.path.join(LOG_DIR, "smartcompress.log")
SKIP_EXTENSIONS = (".gz", ".zlib", ".log", ".tmp")


logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s')

def get_disk_free_percent(path):
    usage = psutil.disk_usage(path)
    return usage.free / usage.total * 100

def should_compress(path):
    try:
        # Never compress our own log, already-compressed files, or logs/temp files
        if os.path.abspath(path) == os.path.abspath(LOG_FILE):
            return False
        return os.path.isfile(path) and not path.endswith(SKIP_EXTENSIONS)
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

def main():
    parser = argparse.ArgumentParser(
        description="Compress the coldest files in a folder when disk space runs low.")
    parser.add_argument("--watch-dir", required=True,
                        help="folder whose files may be compressed")
    parser.add_argument("--disk", default=None,
                        help="path on the disk to monitor (default: the disk holding --watch-dir)")
    parser.add_argument("--threshold", type=float, default=10,
                        help="start compressing below this %% of free space (default: 10)")
    parser.add_argument("--interval", type=int, default=60,
                        help="seconds between checks (default: 60)")
    args = parser.parse_args()

    watch_dir = os.path.expanduser(args.watch_dir)
    if not os.path.isdir(watch_dir):
        parser.error(f"--watch-dir {watch_dir} is not a folder")

    # By default, watch the disk the folder lives on. Inside a snap, "/" is the
    # snap's own read-only file system, not the user's disk.
    disk_path = os.path.expanduser(args.disk) if args.disk else watch_dir

    try:
        monitor_and_compress(watch_dir, disk_path, args.threshold, args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
