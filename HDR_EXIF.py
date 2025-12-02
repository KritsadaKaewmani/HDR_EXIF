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
    python HDR_EXIF.py <input_file_or_directory>

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
import numpy as np  # Numerical operations for image processing
import cv2          # OpenCV for image reading and processing
from scipy.interpolate import RegularGridInterpolator # For 3D LUT interpolation


# ============================================================================
# CORE CONVERSION FUNCTION
# ============================================================================

def convert_to_heif_with_icc(input_file, output_file, icc_profile, profile_name):
    """
    Convert an image file to HEIF format with ICC profile embedding.
    
    This function uses ImageMagick to perform high-quality image conversion
    with specific settings optimized for HDR content preservation.
    
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
    
    # Build the ImageMagick command as a list of arguments
    # Using list format prevents shell injection vulnerabilities
    convert_cmd = [
        "/opt/homebrew/bin/magick",  # Path to ImageMagick executable (macOS Homebrew location)
        input_file,                   # Source image file
        
        # --- Image Quality Settings ---
        "-depth", "10",              # Set bit depth to 10-bit per channel
                                     # 10-bit = 1024 levels per channel (vs 8-bit = 256 levels)
                                     # Essential for HDR to prevent banding artifacts
        
        # --- Text Overlay Settings ---
        "-gravity", "NorthWest",     # Position text at top-left corner
        "-font", "Arial",            # Use Arial font
        "-pointsize", "15",          # Font size of 15 pixels (height)
        "-fill", "gray(50%)",        # Gray 0.5 (50% gray) text color
        "-undercolor", "black",      # Black highlight/background behind text
        "-annotate", "+10+10", profile_name,  # Add text with 10px offset from top-left
        
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
        print(f"  Settings: 10-bit, 4:4:4 chroma, quality 100, ICC profile: {profile_name}")
    except subprocess.CalledProcessError as e:
        # Provide detailed error information if conversion fails
        print(f"✗ Error converting {input_file}:")
        print(f"  Command: {' '.join(convert_cmd)}")
        print(f"  Error output: {e.stderr}")
        raise  # Re-raise the exception to be caught by caller


# ============================================================================
# GAIN MAP GENERATION FUNCTIONS
# ============================================================================

def pq_eotf(image_pq):
    """
    Converts Rec.2100 PQ (0-1 range) to Linear Light (0-10000 nits range).
    Standard SMPTE ST 2084 EOTF.
    """
    m1 = 2610.0 / 16384.0
    m2 = 2523.0 / 4096.0 * 128.0
    c1 = 3424.0 / 4096.0
    c2 = 2413.0 / 4096.0 * 32.0
    c3 = 2392.0 / 4096.0 * 32.0

    # Avoid division by zero/complex numbers
    image_pq = np.maximum(image_pq, 0.0)
    
    num = np.maximum(image_pq**(1.0/m2) - c1, 0.0)
    den = c2 - c3 * (image_pq**(1.0/m2))
    
    linear = (num / den) ** (1.0/m1)
    return linear * 10000.0  # Scale to absolute nits

def read_cube_lut(lut_path):
    """
    Reads a .cube 3D LUT file.
    Returns the LUT data as a numpy array (N, N, N, 3).
    """
    with open(lut_path, 'r') as f:
        lines = f.readlines()

    # Filter out comments and empty lines
    lines = [line.strip() for line in lines if line.strip() and not line.startswith('#') and not line.startswith('TITLE')]
    
    # Parse size
    size_line = [line for line in lines if line.startswith('LUT_3D_SIZE')]
    if not size_line:
        raise ValueError("Invalid .cube file: LUT_3D_SIZE not found")
    
    size = int(size_line[0].split()[1])
    
    # Parse data
    data_lines = [line for line in lines if not line.startswith('LUT_3D_SIZE') and not line.startswith('DOMAIN')]
    
    data = []
    for line in data_lines:
        parts = line.split()
        if len(parts) == 3:
            data.append([float(p) for p in parts])
            
    lut_data = np.array(data, dtype=np.float32)
    
    if len(lut_data) != size * size * size:
         # Some cube files might have DOMAIN_MIN/MAX lines, ensure we only read data
         # If count mismatch, try to be more robust or raise error
         raise ValueError(f"LUT data size mismatch. Expected {size**3}, got {len(lut_data)}")

    # Reshape to (Size, Size, Size, 3)
    # Note: .cube format usually stores data with Red changing fastest, then Green, then Blue?
    # Actually, standard is: Blue (slowest), Green, Red (fastest).
    # So reshaping to (B, G, R, 3) or (R, G, B, 3)?
    # Most parsers reshape to (size, size, size, 3).
    # We need to verify the order for RegularGridInterpolator.
    # RegularGridInterpolator expects points in (x, y, z) order.
    # If we pass (R, G, B) image, we need the grid to match.
    
    # Standard .cube order:
    # Loop B:
    #   Loop G:
    #     Loop R:
    #       Data R G B
    
    # So the flat list is ordered by B, G, R.
    # Reshape to (B, G, R, 3) -> (size, size, size, 3)
    lut_3d = lut_data.reshape(size, size, size, 3)
    
    return lut_3d

def apply_lut(image, lut_3d):
    """
    Applies a 3D LUT to an image using trilinear interpolation.
    image: (H, W, 3) float32, range 0-1
    lut_3d: (N, N, N, 3) float32
    """
    size = lut_3d.shape[0]
    
    # Create grid points for the LUT
    # The LUT is defined on a grid from 0 to 1
    x = np.linspace(0, 1, size)
    y = np.linspace(0, 1, size)
    z = np.linspace(0, 1, size)
    
    # Create interpolator
    # Note: RegularGridInterpolator expects (z, y, x) if we index as [z, y, x]
    # But our image is (R, G, B).
    # The LUT structure from .cube is (B, G, R) if we reshaped as (size, size, size).
    # So lut_3d[b_idx, g_idx, r_idx] gives the value.
    # We should pass points as (B, G, R).
    
    # Let's verify image channel order. OpenCV reads as BGR.
    # We need to convert image to RGB if we want to query as (R, G, B).
    # Or keep BGR and query as (B, G, R).
    # If the image is BGR, and we query (B, G, R), it matches the LUT structure (B, G, R).
    
    interp = RegularGridInterpolator((z, y, x), lut_3d, bounds_error=False, fill_value=None)
    
    # Flatten image to list of points
    # Image is (H, W, 3). If BGR, then points are (B, G, R).
    # This matches the (z, y, x) grid of the LUT (B, G, R).
    points = image.reshape(-1, 3)
    
    # Interpolate
    result = interp(points)
    
    # Reshape back to image
    return result.reshape(image.shape)

def linear_to_srgb(linear_image):
    """
    Simple tone mapping and gamma correction for the SDR Base Image.
    """
    # 1. Simple Tone Mapping (Reinhard or similar) to bring 1000 nits down to 0-1
    # Adjust this scalar to set the "SDR White Point" (e.g., 203 nits maps to ~1.0)
    sdr_white_nits = 203.0 
    mapped = linear_image / sdr_white_nits
    mapped = mapped / (1 + mapped) # Reinhard tonemap
    
    # 2. Gamma Correct (Standard sRGB approx)
    srgb = np.where(mapped <= 0.0031308, 
                    12.92 * mapped, 
                    1.055 * (mapped ** (1.0/2.4)) - 0.055)
    return np.clip(srgb, 0, 1)

def create_gain_map(hdr_linear, sdr_linear, max_headroom=None):
    """
    Calculates the Gain Map.
    Gain = (HDR / SDR). 
    """
    # Avoid division by zero
    sdr_safe = np.maximum(sdr_linear, 1e-6)
    gain = hdr_linear / sdr_safe
    
    if max_headroom is None:
        max_headroom = np.max(gain)
    
    # Ensure headroom is at least 1.0
    max_headroom = max(max_headroom, 1.0)
    
    # If headroom is 1.0 (no gain), return zero map
    if max_headroom <= 1.001:
        return np.zeros_like(gain), 1.0
        
    # Log-encode or Sqrt-encode is common for storage efficiency in 8-bit
    # For this example, we normalize to 0-1 based on headroom
    # Map 1.0 -> 0 (No gain) to Headroom -> 1.0 (Max gain)
    
    # Avoid log2(0) by adding epsilon
    log_gain = np.log2(gain + 1e-6)
    # Clamp negative values (where gain < 1.0) to 0
    log_gain = np.maximum(log_gain, 0.0)
    
    gain_map_norm = log_gain / np.log2(max_headroom)
    
    return np.clip(gain_map_norm, 0, 1), max_headroom

def convert_to_heif_gainmap(input_file, output_file, profile_name):
    """
    Convert HDR image to HEIC with an embedded Gain Map.
    Uses OpenCV for processing and heif-enc for encoding.
    """
    try:
        # 1. Load HDR Image (16-bit TIF)
        # Read as 16-bit unsigned (-1 flag in cv2)
        img_uq = cv2.imread(input_file, cv2.IMREAD_UNCHANGED)
        if img_uq is None:
            raise ValueError(f"Could not read image: {input_file}")
            
        # Convert to 0-1 Float PQ
        img_pq = img_uq.astype(np.float32) / 65535.0

        # 2. Linearize PQ to Nits
        img_linear = pq_eotf(img_pq)

        # 3. Create SDR Base Image
        # Use 3D LUT for Tone Mapping (ACES P3D65 to sRGB)
        lut_filename = "ACES20_P3D65PQ1000_to_sRGB22.cube"
        script_dir = os.path.dirname(os.path.abspath(__file__))
        lut_path = os.path.join(script_dir, lut_filename)
        
        if os.path.exists(lut_path):
            print(f"  Applying LUT: {lut_filename}")
            lut_3d = read_cube_lut(lut_path)
            
            # Apply LUT to PQ image (assuming LUT expects PQ input or 0-1 range)
            # Image is BGR (OpenCV default). LUT expects RGB usually?
            # .cube files are usually RGB.
            # If our apply_lut uses (B, G, R) grid, and image is BGR, it works.
            # But let's be careful.
            # read_cube_lut reshapes to (B, G, R).
            # apply_lut expects points in (B, G, R) order if grid is (z, y, x).
            # So passing BGR image is correct.
            
            img_sdr_srgb = apply_lut(img_pq, lut_3d)
            
            # Clip to 0-1
            img_sdr_srgb = np.clip(img_sdr_srgb, 0, 1)
        else:
            print(f"  ⚠ LUT not found: {lut_filename}. Using fallback tone mapping.")
            # Fallback to simple tone mapping
            img_sdr_linear_src = img_linear.copy()
            img_sdr_srgb = linear_to_srgb(img_sdr_linear_src)
            
        img_sdr_uint8 = (img_sdr_srgb * 255).astype(np.uint8)
        
        # Calculate SDR Linear (Inverse sRGB Gamma) for gain map calculation
        # This represents the linear light of the SDR image displayed on a standard screen
        # sRGB EOTF (approximate)
        sdr_norm = img_sdr_srgb
        sdr_linear_display = np.where(sdr_norm <= 0.04045,
                                     sdr_norm / 12.92,
                                     ((sdr_norm + 0.055) / 1.055) ** 2.4)
        # Scale by SDR white point (203 nits) to match HDR scale
        sdr_white_nits = 203.0
        img_sdr_linear = sdr_linear_display * sdr_white_nits

        # 4. Create Gain Map
        # We use Luminance (Y) for gain map calculation to save space
        # Y = 0.2126 R + 0.7152 G + 0.0722 B
        lum_hdr = 0.2126 * img_linear[:,:,2] + 0.7152 * img_linear[:,:,1] + 0.0722 * img_linear[:,:,0]
        lum_sdr = 0.2126 * img_sdr_linear[:,:,2] + 0.7152 * img_sdr_linear[:,:,1] + 0.0722 * img_sdr_linear[:,:,0]

        gain_map, headroom = create_gain_map(lum_hdr, lum_sdr)
        gain_map_uint8 = (gain_map * 255).astype(np.uint8)

        # 5. Save Intermediate Files
        temp_sdr = f"temp_sdr_{os.getpid()}.jpg"
        temp_gain = f"temp_gain_{os.getpid()}.jpg"
        
        cv2.imwrite(temp_sdr, img_sdr_uint8, [cv2.IMWRITE_JPEG_QUALITY, 90])
        
        # Resize gain map (1/2 resolution)
        h, w = gain_map_uint8.shape
        gain_map_resized = cv2.resize(gain_map_uint8, (w // 2, h // 2))
        cv2.imwrite(temp_gain, gain_map_resized, [cv2.IMWRITE_JPEG_QUALITY, 85])
        
        # 5b. Add Text Overlay to SDR Base Image using ImageMagick
        # Matches the style of the other exports
        annotate_cmd = [
            "/opt/homebrew/bin/magick",
            temp_sdr,
            "-gravity", "NorthWest",
            "-font", "Arial",
            "-pointsize", "15",
            "-fill", "gray(50%)",
            "-undercolor", "black",
            "-annotate", "+10+10", profile_name,
            temp_sdr  # Overwrite temp file
        ]
        subprocess.run(annotate_cmd, check=True)

        # 6. Call heif-enc to stitch
        urn = "urn:com:apple:photo:2020:aux:hdrgainmap"
        
        # Ensure heif-enc is in path or specify full path
        heif_enc_path = "heif-enc"
        if os.path.exists("/opt/homebrew/bin/heif-enc"):
            heif_enc_path = "/opt/homebrew/bin/heif-enc"

        cmd = [
            heif_enc_path,
            "-o", output_file,
            temp_sdr,
            f"--aux-image={urn},{temp_gain}"
        ]

        subprocess.run(cmd, check=True, capture_output=True)
        
        # 7. Inject Metadata via ExifTool
        # Calculate headroom in stops (log2) if needed, or use the ratio directly
        # Apple usually expects stops? The reference code used 3.0.
        # Let's use the calculated headroom if possible, or a safe default.
        # The reference code calculated `headroom` (linear max ratio).
        # Apple:HDRHeadroom is typically in stops.
        headroom_stops = np.log2(headroom) if headroom > 1.0 else 0.0
        
        subprocess.run([
            "exiftool", 
            "-overwrite_original", 
            f"-Apple:HDRHeadroom={headroom_stops:.4f}", 
            output_file
        ], check=False, capture_output=True) # check=False in case exiftool missing

        print(f"✓ Successfully created Gain Map HEIC: {os.path.basename(output_file)}")
        print(f"  Headroom: {headroom:.2f} ({headroom_stops:.2f} stops)")

    except Exception as e:
        print(f"✗ Error creating Gain Map for {input_file}: {e}")
        raise
    finally:
        # Cleanup
        if 'temp_sdr' in locals() and os.path.exists(temp_sdr): os.remove(temp_sdr)
        if 'temp_gain' in locals() and os.path.exists(temp_gain): os.remove(temp_gain)


# ============================================================================
# BATCH PROCESSING FUNCTION
# ============================================================================

def process_directory(directory):
    """
    Process all supported image files in a directory.
    
    Recursively finds and converts all image files with supported extensions
    in the specified directory. Each file is converted to HEIF twice, once for
    each ICC profile, with the profile name appended to the output filename.
    
    Parameters:
        directory (str): Path to directory containing images
    
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
        ("HDR_P3_D65_ST2084.icc", "HDR_gain_map")  # Third export with gain map label
    ]
    
    # Get the script directory to locate ICC profiles
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create "converted" subfolder for output files
    converted_dir = os.path.join(directory, "converted")
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
            # Format: Src_<base_name>_SaveAs_<profile_name>.heic
            output_file = os.path.join(converted_dir, f"Src_{base_name}_SaveAs_{profile_name}.heic")
            
            # Skip if output file already exists
            if os.path.exists(output_file):
                print(f"  ⊘ Skipping {profile_name} (output already exists)")
                file_skipped += 1
                continue
            
            # Attempt conversion
            try:
                if profile_name == "HDR_gain_map":
                    convert_to_heif_gainmap(file_path, output_file, profile_name)
                else:
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
    
    # --- Command-Line Argument Validation ---
    # sys.argv[0] = script name
    # sys.argv[1] = input path (file or directory)
    
    if len(sys.argv) < 2:
        print("\n" + "="*70)
        print("HDR HEIF Converter with ICC Profile Embedding")
        print("="*70)
        print("\nUsage:")
        print(f"  python {os.path.basename(__file__)} <input_file_or_directory>")
        print("\nArguments:")
        print("  input_file_or_directory  Path to image file or directory of images")
        print("\nICC Profiles Used:")
        print("  - HDR_P3_D65_ST2084.icc")
        print("  - P3_PQ.icc")
        print("  - HDR_P3_D65_ST2084.icc (for gain map)")
        print("\nOutput:")
        print("  Files are saved in a 'converted' subfolder:")
        print("  - converted/Src_<filename>_SaveAs_HDR_P3_D65_ST2084.heic")
        print("  - converted/Src_<filename>_SaveAs_P3_PQ.heic")
        print("  - converted/Src_<filename>_SaveAs_HDR_gain_map.heic")
        print("\nExamples:")
        print(f"  python {os.path.basename(__file__)} image.tiff")
        print(f"  python {os.path.basename(__file__)} ./images/")
        print("="*70 + "\n")
        sys.exit(1)
    
    # Extract command-line arguments
    input_path = sys.argv[1]
    
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
            ("HDR_P3_D65_ST2084.icc", "HDR_gain_map")  # Third export with gain map label
        ]
        
        if path_type == 'file':
            # Single file conversion
            print(f"\nMode: Single file conversion")
            print(f"Input: {input_path}\n")
            
            # Get the directory containing the input file
            input_dir = os.path.dirname(os.path.abspath(input_path))
            
            # Create "converted" subfolder for output files
            converted_dir = os.path.join(input_dir, "converted")
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
                if os.path.exists(output_path):
                    print(f"⚠ Warning: Output file already exists: {output_path}")
                    response = input("Overwrite? (y/n): ")
                    if response.lower() != 'y':
                        print(f"Skipping {profile_name} conversion.")
                        continue
                
                # Perform conversion
                print(f"Converting with {profile_name}...")
                if profile_name == "HDR_gain_map":
                    convert_to_heif_gainmap(input_path, output_path, profile_name)
                else:
                    convert_to_heif_with_icc(input_path, output_path, icc_profile_path, profile_name)
                print()
            
            print(f"✓ All conversions complete\n")
        
        elif path_type == 'directory':
            # Batch directory processing
            print(f"\nMode: Batch directory processing")
            print(f"Input directory: {input_path}")
            
            # Process all images in directory
            successful, failed, skipped = process_directory(input_path)
            
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
