import os
import shutil
import re
import cv2
from PIL import Image
from colorama import init, Fore, Style

IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.jpe',
    '.png',
    '.gif',
    '.bmp',
    '.tiff', '.tif',
    '.svg',
    '.webp',
    '.ico',
    '.heic', '.heif',
    '.raw', '.arw', '.cr2', '.nef', '.orf', '.dng', '.raf', '.rw2', '.pef', '.sr2',
    '.jxr'  # JPEG XR
}

VIDEO_EXTENSIONS = {
    '.mp4',
    '.avi',
    '.mkv',
    '.mov',
    '.wmv',
    '.flv',
    '.mpeg', '.mpg',
    '.m4v',
    '.3gp', '.3g2',
    '.vob',
    '.rm', '.rmvb',
    '.m2ts', '.mts', '.ts',
    '.webm',
    '.divx',
    '.xvid',
    '.ogv'
}

AUDIO_EXTENSIONS = {
    '.mp3',
    '.wav',
    '.aac',
    '.flac',
    '.ogg',
    '.wma',
    '.m4a',
    '.opus',
    '.aiff',
    '.alac',
    '.pcm',
    '.amr',
    '.ape',
    '.mka',
    '.ra',
    '.wv',
    '.mid', '.midi',
    '.ac3'
}

MISCELLANEOUS_EXTENSIONS = {
    # Documents
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.odt', '.ods', '.odp', '.rtf', '.txt', '.tex',

    # Archives / Compressed Files
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso', '.dmg',

    # Executables / System Files
    '.exe', '.msi', '.apk', '.bat', '.cmd', '.sh', '.bash', '.app', '.jar',

    # Programming / Markup / Data Files
    '.py', '.js', '.ts', '.html', '.htm', '.css', '.cpp', '.c', '.h', '.hpp',
    '.java', '.rb', '.go', '.rs', '.php', '.pl', '.cs', '.swift', '.kt', '.m',
    '.json', '.xml', '.yml', '.yaml', '.ini', '.cfg', '.conf',

    # E-books
    '.epub', '.mobi', '.azw', '.azw3',

    # 3D Files
    '.stl', '.obj', '.fbx', '.dae',

    # Fonts
    '.ttf', '.otf', '.woff', '.woff2',

    # Others
    '.log', '.csv', '.bak', '.db', '.sql', '.lnk', '.torrent'
}


def get_media_type(file_path: str) -> str:
    """Determine the media type based on the file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in IMAGE_EXTENSIONS:
        return "image"
    elif ext in VIDEO_EXTENSIONS:
        return "video"
    elif ext in AUDIO_EXTENSIONS:
        return "audio"
    elif ext in MISCELLANEOUS_EXTENSIONS:
        return "misc"
    else:
        return "other"


def get_image_resolution(file_path: str):
    """Return the (width, height) of an image file."""
    try:
        with Image.open(file_path) as img:
            return img.size
    except Exception:
        return None


def get_video_resolution(file_path: str):
    """Return the (width, height) of a video file."""
    try:
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            return None
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        return (width, height)
    except Exception:
        return None


def print_success(message: str):
    """Print a message in green to indicate success."""
    print(Fore.GREEN + message + Style.RESET_ALL)


def print_error(message: str):
    """Print a message in red to indicate an error."""
    print(Fore.RED + message + Style.RESET_ALL)


def clean_folder_name(name: str) -> str:
    """
    Clean up a folder name by removing invalid characters.
    If the name starts with a dot, remove it.
    Replace any characters that are not alphanumeric, underscore, or hyphen with an underscore.
    """
    if name.startswith('.'):
        name = name[1:]
    return re.sub(r'[^A-Za-z0-9_\-]', '_', name)


def move_file_to_folder(file_path: str, target_folder: str) -> str:
    """
    Move a file to the target folder.
    If a file with the same name exists, append a counter to the filename.
    Returns the new file path.
    """
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    filename = os.path.basename(file_path)
    dest_path = os.path.join(target_folder, filename)
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(dest_path):
        dest_path = os.path.join(target_folder, f"{base}_{counter}{ext}")
        counter += 1
    shutil.move(file_path, dest_path)
    return dest_path


class FileOrganizer:
    """Handles scanning, sorting, moving, and applying actions to files."""
    
    def __init__(self, root_folder: str):
        self.root_folder = root_folder
        self.files = []         # List of all discovered file paths.
        self.sorted_files = {}  # Dictionary mapping group key to list of file paths.
    
    def scan_files(self):
        """Recursively scan for files in the root folder."""
        for dirpath, _, filenames in os.walk(self.root_folder):
            for file in filenames:
                self.files.append(os.path.join(dirpath, file))
    
    def sort_by_extension(self):
        """Sort files by their file extension."""
        sorted_dict = {}
        for file in self.files:
            ext = os.path.splitext(file)[1].lower() or "no_extension"
            sorted_dict.setdefault(ext, []).append(file)
        self.sorted_files = sorted_dict
    
    def sort_by_media_type(self):
        """Sort files by media type (image, video, audio, other)."""
        sorted_dict = {}
        for file in self.files:
            media_type = get_media_type(file)
            sorted_dict.setdefault(media_type, []).append(file)
        self.sorted_files = sorted_dict
    
    def sort_by_resolution(self):
        """Sort files by resolution (only for images and videos)."""
        sorted_dict = {}
        for file in self.files:
            media_type = get_media_type(file)
            resolution = None
            if media_type == "image":
                resolution = get_image_resolution(file)
            elif media_type == "video":
                resolution = get_video_resolution(file)
            if resolution:
                res_key = f"{resolution[0]}x{resolution[1]}"
            else:
                res_key = "unknown"
            sorted_dict.setdefault(res_key, []).append(file)
        self.sorted_files = sorted_dict
    
    def display_sorted_files(self):
        """Display each group key and the files in that group."""
        for key, files in self.sorted_files.items():
            print(f"Group: {key} ({len(files)} file{'s' if len(files) != 1 else ''})")
            for file in files:
                print(f"  {file}")
            print("")
    
    def move_files_to_hierarchy(self):
        """
        Move each file to a two-level folder structure under the root folder:
          First level: media type (images, videos, audio, others)
          Second level: file extension (without dot) or 'no_extension'
        Returns a dictionary mapping group keys (e.g., 'images/jpg') to lists of new file paths.
        """
        new_locations = {}
        # Iterate over a copy of self.files, since we are moving them
        for file in self.files[:]:
            media_type = get_media_type(file)
            if media_type == "image":
                media_folder = "images"
            elif media_type == "video":
                media_folder = "videos"
            elif media_type == "audio":
                media_folder = "audio"
            elif media_type == "misc":
                media_folder = "misc"
            else:
                media_folder = "others"
            ext = os.path.splitext(file)[1].lower()
            if ext:
                ext_folder = clean_folder_name(ext.lstrip('.'))
            else:
                ext_folder = "no_extension"
            target_folder = os.path.join(self.root_folder, media_folder, ext_folder)
            try:
                dest_path = move_file_to_folder(file, target_folder)
                group_key = os.path.join(media_folder, ext_folder)
                new_locations.setdefault(group_key, []).append(dest_path)
                print_success(f"Moved {file} to {dest_path}")
            except Exception as e:
                print_error(f"Failed to move {file} to {target_folder}: {str(e)}")
        # Update self.files to reflect moved files
        self.files = [f for group in new_locations.values() for f in group]
        return new_locations
    
    def apply_action(self, group_key: str, action):
        """
        Apply the given action function to each file in the specified group.
        The action function should accept two parameters: file_path and index.
        """
        if group_key not in self.sorted_files:
            print_error(f"Group '{group_key}' not found.")
            return
        for idx, file in enumerate(self.sorted_files[group_key], start=1):
            try:
                action(file, idx)
                print_success(f"Action applied to: {file}")
            except Exception as e:
                print_error(f"Failed to apply action on {file}: {str(e)}")


def create_rename_action(new_name_pattern: str):
    """
    Return an action function that renames files using the given pattern.
    Use placeholders in the pattern:
      {basename} - original file name (without extension)
      {index}    - sequential index (starting at 1)
    """
    def action(file_path: str, index: int):
        ext = os.path.splitext(file_path)[1]
        directory = os.path.dirname(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        new_name = new_name_pattern.replace("{basename}", base_name).replace("{index}", str(index))
        new_file_path = os.path.join(directory, new_name + ext)
        os.rename(file_path, new_file_path)
    return action


def create_change_label_action(label: str):
    """
    Return an action function that adds a label as a prefix to the file name.
    """
    def action(file_path: str, index: int):
        directory = os.path.dirname(file_path)
        base_name = os.path.basename(file_path)
        new_name = f"{label}_{base_name}"
        new_file_path = os.path.join(directory, new_name)
        os.rename(file_path, new_file_path)
    return action


def create_add_metadata_action(metadata_key: str, metadata_value: str):
    """
    Return an action function that adds metadata to JPEG images using piexif.
    Note: This action is only supported for JPEG images.
    """
    def action(file_path: str, index: int):
        media_type = get_media_type(file_path)
        if media_type != "image":
            print_error(f"Skipping metadata addition for non-image file: {file_path}")
            return
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in {'.jpg', '.jpeg'}:
            print_error(f"Metadata editing supported only for JPEG images: {file_path}")
            return
        try:
            import piexif
        except ImportError:
            print_error("piexif module not installed. Install it with 'pip install piexif'.")
            return
        try:
            exif_dict = piexif.load(file_path)
        except Exception:
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        from piexif import ImageIFD
        existing = exif_dict["0th"].get(ImageIFD.ImageDescription, b"").decode("utf-8", errors="ignore")
        new_description = f"{existing}; {metadata_key}: {metadata_value}" if existing else f"{metadata_key}: {metadata_value}"
        exif_dict["0th"][ImageIFD.ImageDescription] = new_description.encode("utf-8")
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, file_path)
    return action


def main():
    init(autoreset=True)  # Initialize colorama for colored output
    print("Welcome to the File Organizer!")
    
    folder = input("Enter the folder path to organize: ").strip()
    if not os.path.isdir(folder):
        print_error("Invalid folder path.")
        return

    organizer = FileOrganizer(folder)
    print("Scanning files...")
    organizer.scan_files()
    print_success(f"Found {len(organizer.files)} file{'s' if len(organizer.files) != 1 else ''}.")

    print("\nChoose sorting criteria:")
    print("1. Sort by file extension")
    print("2. Sort by media type")
    print("3. Sort by resolution (images & videos)")
    criteria = input("Enter your choice (1/2/3): ").strip()

    if criteria == "1":
        organizer.sort_by_extension()
    elif criteria == "2":
        organizer.sort_by_media_type()
    elif criteria == "3":
        organizer.sort_by_resolution()
    else:
        print_error("Invalid choice.")
        return

    print("\nSorted files:")
    organizer.display_sorted_files()
    
    move_choice = input("Would you like to move files into a media hierarchy subfolder? (y/n): ").strip().lower()
    if move_choice == 'y':
        new_locations = organizer.move_files_to_hierarchy()
        # Update sorted_files with the new hierarchy groups
        organizer.sorted_files = new_locations

    # Action selection menu
    print("Available actions:")
    print("1. Rename files")
    print("2. Change label (add prefix)")
    print("3. Add metadata (JPEG images only)")
    action_choice = input("Enter action choice (1/2/3) or press Enter to skip actions: ").strip()
    if action_choice not in ["1", "2", "3"]:
        print("No action selected. Exiting.")
        return

    group_key = input("Enter the group key to apply the action (as displayed above): ").strip()
    if action_choice == "1":
        pattern = input("Enter new name pattern (use {basename} for original name and {index} for sequential number): ").strip()
        action_fn = create_rename_action(pattern)
    elif action_choice == "2":
        label = input("Enter label to add as prefix: ").strip()
        action_fn = create_change_label_action(label)
    elif action_choice == "3":
        metadata_key = input("Enter metadata key: ").strip()
        metadata_value = input("Enter metadata value: ").strip()
        action_fn = create_add_metadata_action(metadata_key, metadata_value)

    print("\nApplying action...")
    organizer.apply_action(group_key, action_fn)
    print("Done.")


if __name__ == "__main__":
    main()
