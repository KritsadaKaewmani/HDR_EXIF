#!/usr/bin/env python3
"""
HDR HEIF Converter with ICC Profile Embedding
==============================================

This script converts image files to HEIF (High Efficiency Image Format) with HDR support
and embeds ICC color profiles for accurate color reproduction.

Purpose:
    - Convert images (TIFF, JPEG, PNG) to 10-bit HEIF format
    - Preserve HDR metadata and color information
    - Embed ICC profiles for color-managed workflows
    - Support both single file and batch directory processing

Usage:
    python HDR_EXIF.py <input_file_or_directory> <icc_profile_path>

Requirements:
    - ImageMagick 7+ installed at /opt/homebrew/bin/magick
    - Valid ICC profile file
"""

# ============================================================================
# IMPORTS
# ============================================================================
# Standard library imports for system operations and process management

import os           # Operating system interface for file/directory operations
import subprocess   # Module to spawn new processes and execute shell commands
import sys          # System-specific parameters and functions (command-line args, exit codes)


# ============================================================================
# CORE CONVERSION FUNCTION
# ============================================================================

def convert_to_heif_with_icc(input_file, output_file, icc_profile):
    """
    Convert an image file to HEIF format with ICC profile embedding.
    
    This function uses ImageMagick to perform high-quality image conversion
    with specific settings optimized for HDR content preservation.
    
    Parameters:
        input_file (str): Path to the source image file
        output_file (str): Path where the HEIF file will be saved
        icc_profile (str): Path to the ICC color profile to embed
    
    Technical Details:
        - Bit Depth: 10-bit for HDR support (vs standard 8-bit)
        - Chroma Subsampling: 4:4:4 (no color information loss)
        - Quality: 100 (lossless or near-lossless compression)
        - Orientation: Preserved from source file
    
    Raises:
        subprocess.CalledProcessError: If ImageMagick conversion fails
    """
    
    # Build the ImageMagick command as a list of arguments
    # Using list format prevents shell injection vulnerabilities
    convert_cmd = [
        "/opt/homebrew/bin/magick",  # Path to ImageMagick executable (macOS Homebrew location)
        input_file,                   # Source image file
        
        # --- Image Quality Settings ---
        "-depth", "10",              # Set bit depth to 10-bit per channel
                                     # 10-bit = 1024 levels per channel (vs 8-bit = 256 levels)
                                     # Essential for HDR to prevent banding artifacts
        
        # --- HEIF-Specific Settings ---
        "-define", "heic:preserve-orientation=true",  # Maintain EXIF orientation metadata
                                                       # Ensures image displays correctly rotated
        
        "-define", "heic:chroma=444",  # Use 4:4:4 chroma subsampling
                                       # 4:4:4 = Full color resolution (no subsampling)
                                       # Alternative: 4:2:0 would reduce color data by 50%
                                       # Critical for HDR to preserve color accuracy
        
        "-quality", "100",            # Maximum quality setting (0-100 scale)
                                      # Higher values = less compression = larger files
                                      # 100 ensures minimal quality loss
        
        # --- Color Management ---
        "-profile", icc_profile,      # Embed ICC color profile into the output file
                                      # ICC profiles define color space (e.g., Display P3, Rec.2020)
                                      # Essential for color-accurate display on different devices
        
        output_file                   # Destination file path (.heic extension)
    ]
    
    # Execute the ImageMagick command
    # check=True raises CalledProcessError if command returns non-zero exit code
    try:
        subprocess.run(convert_cmd, check=True, capture_output=True, text=True)
        print(f"✓ Successfully converted: {os.path.basename(input_file)} → {os.path.basename(output_file)}")
        print(f"  Settings: 10-bit, 4:4:4 chroma, quality 100, ICC profile embedded")
    except subprocess.CalledProcessError as e:
        # Provide detailed error information if conversion fails
        print(f"✗ Error converting {input_file}:")
        print(f"  Command: {' '.join(convert_cmd)}")
        print(f"  Error output: {e.stderr}")
        raise  # Re-raise the exception to be caught by caller


# ============================================================================
# BATCH PROCESSING FUNCTION
# ============================================================================

def process_directory(directory, icc_profile):
    """
    Process all supported image files in a directory.
    
    Recursively finds and converts all image files with supported extensions
    in the specified directory. Each file is converted to HEIF with the same
    base name but .heic extension.
    
    Parameters:
        directory (str): Path to directory containing images
        icc_profile (str): Path to ICC profile to embed in all conversions
    
    Supported Formats:
        - TIFF (.tif, .tiff) - Common for professional/HDR workflows
        - JPEG (.jpg, .jpeg) - Standard compressed format
        - PNG (.png) - Lossless compressed format
    
    Returns:
        tuple: (successful_count, failed_count, skipped_count)
    """
    
    # Define supported image file extensions
    # Using lowercase for case-insensitive matching
    SUPPORTED_EXTENSIONS = (".tif", ".tiff", ".jpg", ".jpeg", ".png")
    
    # Initialize counters for processing statistics
    successful = 0
    failed = 0
    skipped = 0
    
    print(f"\n{'='*70}")
    print(f"Processing directory: {directory}")
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
        output_file = os.path.splitext(file_path)[0] + ".heic"
        
        # Skip if output file already exists
        if os.path.exists(output_file):
            print(f"[{idx}/{len(image_files)}] ⊘ Skipping {filename} (output already exists)")
            skipped += 1
            continue
        
        # Attempt conversion
        print(f"[{idx}/{len(image_files)}] Processing: {filename}")
        try:
            convert_to_heif_with_icc(file_path, output_file, icc_profile)
            successful += 1
        except subprocess.CalledProcessError:
            print(f"  ✗ Failed to convert {filename}")
            failed += 1
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            failed += 1
        
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

def validate_icc_profile(icc_profile_path):
    """
    Validate that the ICC profile file exists and is readable.
    
    Parameters:
        icc_profile_path (str): Path to ICC profile file
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not os.path.isfile(icc_profile_path):
        print(f"✗ Error: ICC profile not found: {icc_profile_path}")
        return False
    
    if not os.access(icc_profile_path, os.R_OK):
        print(f"✗ Error: ICC profile is not readable: {icc_profile_path}")
        return False
    
    # Check file extension (common ICC extensions)
    if not icc_profile_path.lower().endswith(('.icc', '.icm')):
        print(f"⚠ Warning: File may not be an ICC profile (expected .icc or .icm extension)")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return False
    
    return True


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
    
    # --- Command-Line Argument Validation ---
    # sys.argv[0] = script name
    # sys.argv[1] = input path (file or directory)
    # sys.argv[2] = ICC profile path
    
    if len(sys.argv) < 3:
        print("\n" + "="*70)
        print("HDR HEIF Converter with ICC Profile Embedding")
        print("="*70)
        print("\nUsage:")
        print(f"  python {os.path.basename(__file__)} <input_file_or_directory> <icc_profile>")
        print("\nArguments:")
        print("  input_file_or_directory  Path to image file or directory of images")
        print("  icc_profile              Path to ICC color profile (.icc or .icm)")
        print("\nExamples:")
        print(f"  python {os.path.basename(__file__)} image.tiff Display-P3.icc")
        print(f"  python {os.path.basename(__file__)} ./images/ Rec2020-PQ.icc")
        print("="*70 + "\n")
        sys.exit(1)
    
    # Extract command-line arguments
    input_path = sys.argv[1]
    icc_profile = sys.argv[2]
    
    # --- Validate ICC Profile ---
    if not validate_icc_profile(icc_profile):
        sys.exit(1)
    
    # --- Validate Input Path ---
    path_type = validate_input_path(input_path)
    if path_type is None:
        sys.exit(1)
    
    # --- Process Based on Input Type ---
    try:
        if path_type == 'file':
            # Single file conversion
            print(f"\nMode: Single file conversion")
            print(f"Input: {input_path}")
            print(f"ICC Profile: {icc_profile}\n")
            
            # Generate output filename (same name, .heic extension)
            output_path = os.path.splitext(input_path)[0] + ".heic"
            
            # Check if output already exists
            if os.path.exists(output_path):
                print(f"⚠ Warning: Output file already exists: {output_path}")
                response = input("Overwrite? (y/n): ")
                if response.lower() != 'y':
                    print("Conversion cancelled.")
                    sys.exit(0)
            
            # Perform conversion
            convert_to_heif_with_icc(input_path, output_path, icc_profile)
            print(f"\n✓ Conversion complete: {output_path}\n")
        
        elif path_type == 'directory':
            # Batch directory processing
            print(f"\nMode: Batch directory processing")
            print(f"Input directory: {input_path}")
            print(f"ICC Profile: {icc_profile}")
            
            # Process all images in directory
            successful, failed, skipped = process_directory(input_path, icc_profile)
            
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
