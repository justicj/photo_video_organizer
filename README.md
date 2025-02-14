# photo_video_organizer

photo_video_organizer is a Python script to organize a directory of photos and videos using EXIF and metadata.  
It is currently written for use in Windows only.  

## Features

- Organizes photos and videos into folders by date
- Supports various file formats (JPEG, PNG, MP4, etc.)
- Uses EXIF data to determine the date taken for photos
- Uses metadata to determine the date created for videos
- Handles files without EXIF or metadata by using the file creation date

## Requirements

- Windows OS Only
- Python 3.x
- Pillow library
- pillow_heif library

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/photo_video_organizer.git
    ```
2. Navigate to the project directory:
    ```sh
    cd photo_video_organizer
    ```
3. Install the required libraries:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Place the photos and videos you want to organize in a directory.
2. Run the script:
    ```sh
    python .\organize.py "F:\source" "F:\destination"
    ```
3. The script will create folders by date and move the files accordingly.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
