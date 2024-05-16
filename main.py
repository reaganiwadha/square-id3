import os
import argparse
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error, ID3NoHeaderError
from PIL import Image
from io import BytesIO

def crop_center_square(image):
    """Crop the center square of the image."""
    width, height = image.size
    new_edge_length = min(width, height)
    left = (width - new_edge_length) // 2
    top = (height - new_edge_length) // 2
    right = (width + new_edge_length) // 2
    bottom = (height + new_edge_length) // 2
    return image.crop((left, top, right, bottom))

def process_mp3_file(file_path):
    """Process a single MP3 file to crop its album art to 1:1."""
    try:
        audio = MP3(file_path, ID3=ID3)
    except ID3NoHeaderError:
        print(f"Skipping {file_path}: No ID3 tag.")
        return
    
    if not audio.tags:
        print(f"Skipping {file_path}: No tags found.")
        return

    apic_tags = [tag for tag in audio.tags.values() if isinstance(tag, APIC)]
    
    if not apic_tags:
        print(f"Skipping {file_path}: No APIC (album art) tag found.")
        return

    for apic in apic_tags:
        try:
            image_data = apic.data
            image = Image.open(BytesIO(image_data))
            
            if image.width == image.height:
                print(f"Skipping {file_path}: Image is already 1:1 aspect ratio.")
                return
            
            cropped_image = crop_center_square(image)
            output = BytesIO()
            cropped_image.save(output, format='JPEG')
            apic.data = output.getvalue()
            
            audio.save()
            print(f"Processed {file_path}: Album art cropped to 1:1.")
            return  # Stop after processing the first APIC tag
        except Exception as e:
            print(f"Error processing album art in {file_path}: {e}")

def process_folder(folder_path):
    """Process all MP3 files in the given folder."""
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.mp3'):
            file_path = os.path.join(folder_path, filename)
            process_mp3_file(file_path)

def main():
    parser = argparse.ArgumentParser(description='Crop center 1:1 the image art of MP3 files in a folder.')
    parser.add_argument('folder', help='Path to the folder containing MP3 files')
    args = parser.parse_args()

    process_folder(args.folder)

if __name__ == "__main__":
    main()

