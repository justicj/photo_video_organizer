import os
from datetime import datetime
import argparse
import subprocess
import sys
import json
import requests
from PIL import Image
from PIL.ExifTags import TAGS
from pillow_heif import register_heif_opener

PICTURE_FILE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".heic"]
MOVIE_FILE_EXTENSIONS = [".mov", ".mp4"]
LIVE_PHOTO_DURATION = 3.5
FFPROBE_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip"
FFPROBE_PATH = "./ffmpeg-master-latest-win64-gpl-shared/bin/ffprobe.exe"


def get_date_from_timestamp(file):
    print(f"Date determined by file creation time: {file}")
    creation_time = os.path.getctime(file)
    return datetime.fromtimestamp(creation_time).strftime("%Y:%m:%d %H:%M:%S")


def get_photo_exif_date(file):
    with Image.open(file) as img:
        file_ext = os.path.splitext(file)[1]
        if file_ext.lower() == ".heic":
            exif_data = img.getexif()
        else:
            exif_data = img._getexif()
        if exif_data:
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name == "DateTimeOriginal":
                    return value
        # if nothing is found, return the file creation time
        return get_date_from_timestamp(file)


def get_video_exif_date(video_path):
    video_path = video_path.replace("\\\\", "\\")
    try:
        command = [
            FFPROBE_PATH,
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-i",
            video_path,
        ]
        result = subprocess.run(
            command, capture_output=True, text=True, check=True
        )
        metadata = json.loads(result.stdout)
        creation_time = metadata["format"]["tags"].get("creation_time")
        duration = metadata["format"].get("duration")
        return creation_time, duration
    except (
        subprocess.CalledProcessError,
        KeyError,
        json.JSONDecodeError,
    ) as e:
        print(f"Error extracting creation time: {e}")
        return None, None


def format_date(date_str, date_format):
    if date_str is not None and date_str != "0000:00:00 00:00:00":
        try:
            date = datetime.strptime(date_str, date_format)
            return date
        except ValueError:
            # print(f"Error converting date: {date_str}")
            return None
    return None


def move_live_photo(file):
    print(f"Video looks like a live photo: {file}")
    destination_directory = f"{DESTINATION_PICTURE_DIRECTORY}\\live_photo"
    os.makedirs(destination_directory, exist_ok=True)
    os.rename(
        file,
        os.path.join(destination_directory, os.path.basename(file)),
    )
    return True


def move_file(file, file_type, date):
    if date is None:
        destination_directory = (
            f"{DESTINATION_PICTURE_DIRECTORY}\\{file_type}\\no_date"
        )
    else:
        year = date.year
        month = date.month
        destination_directory = f"{DESTINATION_PICTURE_DIRECTORY}\\{file_type}\\{year}\\{month:02d}"
    os.makedirs(destination_directory, exist_ok=True)
    os.rename(
        file, os.path.join(destination_directory, os.path.basename(file))
    )
    return date is not None


def organize_file(file, file_type):
    date = None
    if file_type == "photo":
        date_str = get_photo_exif_date(file)
        date = format_date(date_str, "%Y:%m:%d %H:%M:%S")
    elif file_type == "video":
        date_str, duration = get_video_exif_date(file)
        if duration:
            if float(duration) < LIVE_PHOTO_DURATION:
                return move_live_photo(file)
        date = format_date(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        if date is None:
            date = format_date(date_str, "%Y-%m-%dT%H:%M:%SZ")

    return move_file(file, file_type, date)


def download_tools():
    print("Downloading ffmpeg tools")
    r = requests.get(FFPROBE_URL, timeout=90)
    with open("ffmpeg.zip", "wb") as f:
        f.write(r.content)
        with zipfile.ZipFile("ffmpeg.zip", "r") as zip_ref:
            zip_ref.extractall()
    os.remove("ffmpeg.zip")


def main():
    successful = []
    no_date = []
    unssupported = []
    result = False
    source_files = os.listdir(SOURCE_PICTURE_DIRECTORY)
    print(f"Total files to process: {len(source_files)}")
    for file in source_files:
        if file.lower().endswith(tuple(PICTURE_FILE_EXTENSIONS)):
            result = organize_file(
                f"{SOURCE_PICTURE_DIRECTORY}\\{file}", "photo"
            )
        elif file.lower().endswith(tuple(MOVIE_FILE_EXTENSIONS)):
            result = organize_file(
                f"{SOURCE_PICTURE_DIRECTORY}\\{file}", "video"
            )
        else:
            unssupported.append(file)
            continue
        if result:
            successful.append(file)
        else:
            no_date.append(file)
    print(f"Files successfully organized: {len(successful)}")
    print(f"Files with no date: {len(no_date)}")
    print(f"Unsupported files: {len(unssupported)}")


if __name__ == "__main__":
    register_heif_opener()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source_directory",
        help="Source directory containing photos and videos to organize eg: 'F:\\photos'",
    )
    parser.add_argument(
        "destination_directory",
        help="Destination directory to move organized photos and videos eg: 'F:\\organized_photos'",
    )
    args = parser.parse_args()
    if not args.source_directory or not args.destination_directory:
        print("Please provide source and destination directories")
        sys.exit()
    SOURCE_PICTURE_DIRECTORY = args.source_directory
    DESTINATION_PICTURE_DIRECTORY = args.destination_directory
    SOURCE_PICTURE_DIRECTORY = SOURCE_PICTURE_DIRECTORY.replace("\\", "\\\\")
    DESTINATION_PICTURE_DIRECTORY = DESTINATION_PICTURE_DIRECTORY.replace(
        "\\", "\\\\"
    )
    if not os.path.exists(SOURCE_PICTURE_DIRECTORY):
        print(f"Source directory {SOURCE_PICTURE_DIRECTORY} does not exist")
        sys.exit()
    print(
        f"Organizing files from {SOURCE_PICTURE_DIRECTORY} to {DESTINATION_PICTURE_DIRECTORY}"
    )
    if not os.path.exists(FFPROBE_PATH):
        import zipfile

        download_tools()
    main()
