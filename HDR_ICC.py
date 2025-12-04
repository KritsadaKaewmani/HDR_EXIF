#!/usr/bin/env python3

"""
HDR HEIC Converter with ICC Profile Embedding
==============================================

This script converts image files to HEIF (High Efficiency Image Format) with HDR support
and embeds ICC color profiles for accurate color reproduction.

Purpose:
    - Convert images (TIFF, JPEG, PNG) to 10-bit HEIF format
    - Preserve HDR metadata and color information
    - Embed ICC profiles for color-managed workflows
    - Support both single file and batch directory processing

Usage:
    python HDR_ICC.py <input_file_or_directory>

Requirements:
    - ImageMagick 7+ installed at /opt/homebrew/bin/magick
    - Valid ICC profile files (HDR_P3_D65_ST2084.icc, P3_PQ.icc)
"""

# ============================================================================
# IMPORTS
# ============================================================================

import os           # Operating system interface for file/directory operations
import subprocess   # Module to spawn new processes and execute shell commands
import sys          # System-specific parameters and functions (command-line args, exit codes)


# ============================================================================
# CORE CONVERSION FUNCTION
# ============================================================================

def convert_to_heif_with_icc(input_file, output_file, icc_profile, profile_name):
    """
    Convert an image file to HEIF format with proper ICC profile handling.
    
    This function uses ImageMagick to perform high-quality image conversion.
    
    Color Management Strategy:
        - Always strip any existing ICC profiles
        - Embed the target HDR ICC profile
        - This preserves the original pixel data (no color space conversion)
        - Ensures consistent results regardless of source file tagging
    
    This prevents "double HDR to SDR" conversion issues where ImageMagick
    might incorrectly tone-map HDR content during conversion.
    
    Parameters:
        input_file (str): Path to the source image file
        output_file (str): Path where the HEIF file will be saved
        icc_profile (str): Path to the ICC color profile to embed
        profile_name (str): Name of the ICC profile for display purposes
    
    Technical Details:
        - Bit Depth: 10-bit for HDR support (vs standard 8-bit)
        - Chroma Subsampling: 4:4:4 (no color information loss)
        - Quality: 100 (lossless or near-lossless compression)
        - Orientation: Preserved from source file
    
    Raises:
        subprocess.CalledProcessError: If ImageMagick conversion fails
    """
    
    # Build the ImageMagick command
    convert_cmd = [
        "/opt/homebrew/bin/magick",
        input_file,
        
        # --- Image Quality Settings ---
        "-depth", "10",              # Set bit depth to 10-bit per channel
        
        # --- Text Overlay Settings ---
        "-gravity", "NorthWest",
        "-font", "Arial",
        "-pointsize", "15",
        "-fill", "gray(50%)",
        "-undercolor", "black",
        "-annotate", "+10+10", profile_name,
        
        # --- HEIF-Specific Settings ---
        "-define", "heic:preserve-orientation=true",
        "-define", "heic:chroma=444",
        "-quality", "100",
    ]
    
    # --- Color Management Strategy ---
    # We always strip the source profile and embed the target profile.
    # This preserves the original pixel data and simply "tags" it with the correct HDR profile.
    # This avoids issues where ImageMagick might incorrectly convert/tone-map HDR content.
    convert_cmd.extend([
        "+profile", "*",          # Strip all existing profiles
        "-profile", icc_profile,  # Embed target profile
    ])
    color_strategy = "Profile embedding (preserve pixels)"
    
    convert_cmd.append(output_file)
    
    # Execute the ImageMagick command
    try:
        subprocess.run(convert_cmd, check=True, capture_output=True, text=True)
        print(f"✓ Successfully converted: {os.path.basename(input_file)} → {os.path.basename(output_file)}")
        print(f"  Settings: 10-bit, 4:4:4 chroma, quality 100, ICC profile: {profile_name}")
        print(f"  Color management: {color_strategy}")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error converting {input_file}:")
        print(f"  Command: {' '.join(convert_cmd)}")
        print(f"  Error output: {e.stderr}")
        raise


# ============================================================================
# BATCH PROCESSING FUNCTION
# ============================================================================

def process_directory(directory, overwrite=False):
    """
    Process all supported image files in a directory.
    
    Recursively finds and converts all image files with supported extensions
    in the specified directory. Each file is converted to HEIF with each
    ICC profile, with the profile name appended to the output filename.
    
    Parameters:
        directory (str): Path to directory containing images
        overwrite (bool): If True, overwrite existing files without prompting
    
    Supported Formats:
        - TIFF (.tif, .tiff) - Common for professional/HDR workflows
        - JPEG (.jpg, .jpeg) - Standard compressed format
        - PNG (.png) - Lossless compressed format
    
    Returns:
        tuple: (successful_count, failed_count, skipped_count)
    """
    
    # Define ICC profiles to use for conversion
    # Each tuple contains (profile_filename, profile_display_name)
    ICC_PROFILES = [
        ("HDR_P3_D65_ST2084.icc", "HDR_P3_D65_ST2084"),
        ("P3_PQ.icc", "P3_PQ"),
    ]
    
    # Get the script directory to locate ICC profiles
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create "converted_with_ICC" folder at the same level as the source directory
    parent_dir = os.path.dirname(os.path.abspath(directory))
    converted_dir = os.path.join(parent_dir, "converted_with_ICC")
    os.makedirs(converted_dir, exist_ok=True)
    
    # Define supported image file extensions
    # Using lowercase for case-insensitive matching
    SUPPORTED_EXTENSIONS = (".tif", ".tiff", ".jpg", ".jpeg", ".png")
    
    # Initialize counters for processing statistics
    successful = 0
    failed = 0
    skipped = 0
    
    print(f"\n{'='*70}")
    print(f"Processing directory: {directory}")
    print(f"Overwrite mode: {'Enabled' if overwrite else 'Disabled'}")
    print(f"{'='*70}\n")
    
    # Get list of all files in directory
    try:
        files = os.listdir(directory)
    except PermissionError:
        print(f"✗ Error: Permission denied to access directory: {directory}")
        return (0, 0, 0)
    
    # Filter and process only image files
    image_files = [f for f in files if f.lower().endswith(SUPPORTED_EXTENSIONS)]
    
    if not image_files:
        print(f"⚠ No supported image files found in {directory}")
        print(f"  Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}")
        return (0, 0, 0)
    
    print(f"Found {len(image_files)} image file(s) to process\n")
    
    # Process each image file
    for idx, filename in enumerate(image_files, 1):
        # Construct full file paths
        file_path = os.path.join(directory, filename)
        base_name = os.path.splitext(filename)[0]
        
        print(f"[{idx}/{len(image_files)}] Processing: {filename}")
        
        # Convert with each ICC profile
        file_successful = 0
        file_failed = 0
        file_skipped = 0
        
        for profile_filename, profile_name in ICC_PROFILES:
            # Construct ICC profile path
            icc_profile_path = os.path.join(script_dir, profile_filename)
            
            # Validate ICC profile exists
            if not os.path.isfile(icc_profile_path):
                print(f"  ✗ ICC profile not found: {profile_filename}")
                file_failed += 1
                continue
            
            # Construct output filename
            output_file = os.path.join(converted_dir, f"Src_{base_name}_SaveAs_{profile_name}.heic")
            
            # Skip if output file already exists and overwrite is not enabled
            if os.path.exists(output_file) and not overwrite:
                print(f"  ⊘ Skipping {profile_name} (output already exists)")
                file_skipped += 1
                continue
            
            # Attempt conversion
            try:
                convert_to_heif_with_icc(file_path, output_file, icc_profile_path, profile_name)
                file_successful += 1
            except subprocess.CalledProcessError:
                print(f"  ✗ Failed to convert with {profile_name}")
                file_failed += 1
            except Exception as e:
                print(f"  ✗ Unexpected error with {profile_name}: {e}")
                file_failed += 1
        
        # Update overall counters
        if file_successful > 0:
            successful += file_successful
        if file_failed > 0:
            failed += file_failed
        if file_skipped > 0:
            skipped += file_skipped
        
        print()  # Blank line for readability
    
    # Print summary statistics
    print(f"{'='*70}")
    print(f"Processing complete!")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Skipped: {skipped}")
    print(f"{'='*70}\n")
    
    return (successful, failed, skipped)


# ============================================================================
# INPUT VALIDATION FUNCTIONS
# ============================================================================

def validate_icc_profiles():
    """
    Validate that the required ICC profile files exist and are readable.
    
    Returns:
        bool: True if all profiles are valid, False otherwise
    """
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define required ICC profiles
    required_profiles = ["HDR_P3_D65_ST2084.icc", "P3_PQ.icc"]
    
    all_valid = True
    for profile_filename in required_profiles:
        icc_profile_path = os.path.join(script_dir, profile_filename)
        
        if not os.path.isfile(icc_profile_path):
            print(f"✗ Error: ICC profile not found: {profile_filename}")
            print(f"  Expected location: {icc_profile_path}")
            all_valid = False
            continue
        
        if not os.access(icc_profile_path, os.R_OK):
            print(f"✗ Error: ICC profile is not readable: {profile_filename}")
            all_valid = False
            continue
        
        print(f"✓ Found ICC profile: {profile_filename}")
    
    return all_valid


def validate_input_path(input_path):
    """
    Validate that the input path exists and is accessible.
    
    Parameters:
        input_path (str): Path to file or directory
    
    Returns:
        str: 'file', 'directory', or None if invalid
    """
    if not os.path.exists(input_path):
        print(f"✗ Error: Input path does not exist: {input_path}")
        return None
    
    if os.path.isfile(input_path):
        return 'file'
    elif os.path.isdir(input_path):
        return 'directory'
    else:
        print(f"✗ Error: Input path is neither a file nor directory: {input_path}")
        return None


# ============================================================================
# MAIN EXECUTION BLOCK
# ============================================================================

def main():
    """
    Main entry point for the script.
    
    Handles command-line argument parsing, validation, and orchestrates
    the conversion process for either single files or directories.
    """
    
    # --- Command-Line Argument Parsing ---
    import argparse
    
    parser = argparse.ArgumentParser(
        description="HDR HEIC Converter with ICC Profile Embedding",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "input_path",
        help="Path to image file or directory of images"
    )
    
    parser.add_argument(
        "-o", "--overwrite",
        action="store_true",
        help="Overwrite existing output files without prompting"
    )
    
    # If no arguments provided, print custom help and exit
    if len(sys.argv) < 2:
        print("\n" + "="*70)
        print("HDR HEIC Converter with ICC Profile Embedding")
        print("="*70)
        print("\nUsage:")
        print(f"  python {os.path.basename(__file__)} [-o] <input_file_or_directory>")
        print("\nArguments:")
        print("  input_file_or_directory  Path to image file or directory of images")
        print("  -o, --overwrite          Overwrite existing output files without prompting")
        print("\nICC Profiles Used:")
        print("  - HDR_P3_D65_ST2084.icc")
        print("  - P3_PQ.icc")
        print("\nOutput:")
        print("  Files are saved in a 'converted_with_ICC' subfolder:")
        print("  - converted_with_ICC/Src_<filename>_SaveAs_HDR_P3_D65_ST2084.heic")
        print("  - converted_with_ICC/Src_<filename>_SaveAs_P3_PQ.heic")
        print("\nExamples:")
        print(f"  python {os.path.basename(__file__)} image.tiff")
        print(f"  python {os.path.basename(__file__)} -o ./images/")
        print("="*70 + "\n")
        sys.exit(1)
        
    args = parser.parse_args()
    input_path = args.input_path
    overwrite = args.overwrite
    
    # --- Validate ICC Profiles ---
    print("\nValidating ICC profiles...")
    if not validate_icc_profiles():
        print("\n✗ ICC profile validation failed. Please ensure the required ICC profiles are in the script directory.")
        sys.exit(1)
    print()
    
    # --- Validate Input Path ---
    path_type = validate_input_path(input_path)
    if path_type is None:
        sys.exit(1)
    
    # --- Process Based on Input Type ---
    try:
        # Get the script directory to locate ICC profiles
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Define ICC profiles
        ICC_PROFILES = [
            ("HDR_P3_D65_ST2084.icc", "HDR_P3_D65_ST2084"),
            ("P3_PQ.icc", "P3_PQ"),
        ]
        
        if path_type == 'file':
            # Single file conversion
            print(f"\nMode: Single file conversion")
            print(f"Input: {input_path}")
            print(f"Overwrite mode: {'Enabled' if overwrite else 'Disabled'}\n")
            
            # Get the directory containing the input file
            input_dir = os.path.dirname(os.path.abspath(input_path))
            
            # Create "converted_with_ICC" folder at the same level as the source directory
            parent_dir = os.path.dirname(input_dir)
            converted_dir = os.path.join(parent_dir, "converted_with_ICC")
            os.makedirs(converted_dir, exist_ok=True)
            
            # Get base filename without extension
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            
            # Convert with each ICC profile
            for profile_filename, profile_name in ICC_PROFILES:
                # Construct ICC profile path
                icc_profile_path = os.path.join(script_dir, profile_filename)
                
                # Generate output filename with profile name appended in converted subfolder
                # Format: Src_<base_name>_SaveAs_<profile_name>.heic
                output_path = os.path.join(converted_dir, f"Src_{base_name}_SaveAs_{profile_name}.heic")
                
                # Check if output already exists
                if os.path.exists(output_path) and not overwrite:
                    print(f"⚠ Warning: Output file already exists: {output_path}")
                    response = input("Overwrite? (y/n): ")
                    if response.lower() != 'y':
                        print(f"Skipping {profile_name} conversion.")
                        continue
                
                # Perform conversion
                print(f"Converting with {profile_name}...")
                convert_to_heif_with_icc(input_path, output_path, icc_profile_path, profile_name)
                print()
            
            print(f"✓ All conversions complete\n")
        
        elif path_type == 'directory':
            # Batch directory processing
            print(f"\nMode: Batch directory processing")
            print(f"Input directory: {input_path}")
            
            # Process all images in directory
            successful, failed, skipped = process_directory(input_path, overwrite=overwrite)
            
            # Exit with error code if any conversions failed
            if failed > 0:
                sys.exit(1)
    
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\n\n⚠ Conversion interrupted by user")
        sys.exit(130)  # Standard exit code for SIGINT
    
    except Exception as e:
        # Catch any unexpected errors
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    """
    This block ensures main() only runs when script is executed directly,
    not when imported as a module.
    
    This is Python best practice for creating reusable, testable code.
    """
    main()
