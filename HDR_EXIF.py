import os
import subprocess
import sys

def convert_to_heif_with_icc(input_file, output_file, icc_profile):
    # ImageMagick command to convert the image to HEIF 10-bit with custom settings and embed the ICC profile
    convert_cmd = [
        "/opt/homebrew/bin/magick", 
        input_file,
        "-depth", "10",  # 10-bit depth
        "-define", "heic:preserve-orientation=true",  # Preserve orientation
        "-define", "heic:chroma=444",  # Use 4:4:4 chroma subsampling
        "-quality", "100",  # Set the quality to maximum
        "-profile", icc_profile,  # Embed ICC profile
        output_file
    ]

    # Run the ImageMagick command
    subprocess.run(convert_cmd, check=True)
    print(f"Converted {input_file} to {output_file} (HEIF 10-bit with custom settings and ICC profile)")

def process_directory(directory, icc_profile):
    for filename in os.listdir(directory):
        if filename.lower().endswith((".tif", ".tiff", ".jpg", ".jpeg", ".png")):  # Add more extensions as needed
            file_path = os.path.join(directory, filename)
            output_file = os.path.splitext(file_path)[0] + ".heic"
            convert_to_heif_with_icc(file_path, output_file, icc_profile)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python convert_and_embed_icc.py <input_file_or_directory> <icc_profile>")
        sys.exit(1)

    input_path = sys.argv[1]
    icc_profile = sys.argv[2]

    if not os.path.isfile(icc_profile):
        print(f"The ICC profile '{icc_profile}' does not exist.")
        sys.exit(1)

    if os.path.isfile(input_path):
        # Convert and embed ICC profile for a single file
        output_path = os.path.splitext(input_path)[0] + ".heic"
        convert_to_heif_with_icc(input_path, output_path, icc_profile)
    elif os.path.isdir(input_path):
        # Process all image files in the directory
        process_directory(input_path, icc_profile)
    else:
        print("The specified path is neither a file nor a directory.")
        sys.exit(1)
