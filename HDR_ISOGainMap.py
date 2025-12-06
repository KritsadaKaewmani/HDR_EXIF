#!/usr/bin/env python3

import os
import subprocess
import sys
import numpy as np
import cv2
from scipy.interpolate import RegularGridInterpolator

def normalized_pq_to_absolute_nits(image_pq):
    """
    Converts Rec.2100 PQ (0-1 range) to Linear Light (0-10000 nits range).
    Standard SMPTE ST 2084 EOTF.
    """
    m1 = (2610.0 / 16384.0)
    m2 = (2523.0 / 4096.0) * 128.0
    c1 = (3424.0 / 4096.0)
    c2 = (2413.0 / 4096.0) * 32.0
    c3 = (2392.0 / 4096.0) * 32.0

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
        raise ValueError(f"LUT data size mismatch. Expected {size**3}, got {len(lut_data)}")

    # Reshape to (Size, Size, Size, 3)
    # .cube format is Red fastest, then Green, then Blue
    # So numpy reshape (C-order) gives [Blue, Green, Red, 3]
    lut_3d = lut_data.reshape(size, size, size, 3)
    
    # Transpose to [Red, Green, Blue, 3] so that (r, g, b) indices work correctly
    lut_3d = lut_3d.transpose(2, 1, 0, 3)
    
    return lut_3d

def apply_lut(image, lut_3d):
    """
    Applies a 3D LUT to an image using trilinear interpolation.
    image: (H, W, 3) float32, range 0-1
    lut_3d: (N, N, N, 3) float32

    img is in float32 (0-1)
    and check BGR to RGB order
    """

    size = lut_3d.shape[0]
    
    # Create grid points for the LUT
    x = np.linspace(0, 1, size)
    y = np.linspace(0, 1, size)
    z = np.linspace(0, 1, size)
    
    interp = RegularGridInterpolator((z, y, x), lut_3d, bounds_error=False, fill_value=None)
    
    # Flatten image to list of points
    points = image.reshape(-1, 3)
    
    # Interpolate
    result = interp(points)
    
    # Reshape back to image
    return result.reshape(image.shape)


def export_gain_map_png(img_hdr_linear_absolute_nits, img_sdr_linear_absolute_nits, estimated_headroom, output_path):

    """    
    Process:
        1. Calculate gain ratio per pixel (HDR / SDR)
        2. Normalize to 0-1 range based on headroom
        3. Apply Rec.709 gamma (2.2) encoding
        4. Save as 8-bit grayscale PNG for Core Image
    """
    
    img_sdr_linear_safe = np.maximum(img_sdr_linear_absolute_nits, 1e-6)
    gain_map = img_hdr_linear_absolute_nits / img_sdr_linear_safe
    
    gain_map_normalized = (gain_map - 1.0) / max(estimated_headroom - 1.0, 0.001)
    gain_map_normalized = np.clip(gain_map_normalized, 0, 1)
 
    gain_map_gamma = np.power(gain_map_normalized, 1.0 / 2.2)

    if len(gain_map_gamma.shape) == 3:
        gain_map_gray = np.mean(gain_map_gamma, axis=2)
    else:
        gain_map_gray = gain_map_gamma
    
    gain_map_uint8 = (gain_map_gray * 255).astype(np.uint8)
    cv2.imwrite(output_path, gain_map_uint8)
    
    print(f"  ✓ tmp gain map saved for visual check: {output_path}")


def convert_to_avif_gainmap(input_file, output_file):
    
    str_filepath_sdr_srgb_from_LUT = f"temp_sdr_{os.getpid()}.tif"

    try:
        # ====================================================================
        # DATA FLOW: Image Loading and Transformation Pipeline
        # ====================================================================
        # input_file (string: file path to 16-bit TIFF)
        #     ↓ cv2.imread(IMREAD_UNCHANGED)
        # img_p3_pq (uint16: 0-65535, "unsigned quantized")
        #     ↓ astype(float32) / 65535.0
        # img_P3_linear_absolute_nits (float32: 0-10000, "P3 D65 absolute luminance")
        # ====================================================================
        
        img_p3_pq_U16 = cv2.imread(input_file, cv2.IMREAD_UNCHANGED)
        if img_p3_pq_U16 is None:
            raise ValueError(f"Could not read converted image: {input_file}")
        img_p3_pq_normalized_float = img_p3_pq_U16.astype(np.float32) / 65535.0
        img_P3_linear_absolute_nits = normalized_pq_to_absolute_nits(img_p3_pq_normalized_float)
        hdr_max_nits = np.max(img_P3_linear_absolute_nits)
        print(f"  HDR Max Nits: {hdr_max_nits:.2f}")
    
        
        # Generate SDR using ACES LUT 
        lut_filename = "ACES20_P3D65PQ1000D60_to_sRGBPW.cube"
        script_dir = os.path.dirname(os.path.abspath(__file__))
        lut_path = os.path.join(script_dir, lut_filename)
        
        if os.path.exists(lut_path):
            print(f"  Applying LUT for SDR base: {lut_filename}")
            lut_3d = read_cube_lut(lut_path)
                
            # Apply LUT (P3 PQ → sRGB gamma), convert to float32, and clip
            img_sdr_srgb_normalized_float = np.clip(apply_lut(img_p3_pq_normalized_float, lut_3d).astype(np.float32), 0, 1)

            # Save SDR temp file for Swift conversion
            cv2.imwrite(str_filepath_sdr_srgb_from_LUT, img_sdr_srgb_normalized_float)
                
            # Calculate Headroom
            sdr_linear_display = np.where(img_sdr_srgb_normalized_float <= 0.04045,
                                     img_sdr_srgb_normalized_float / 12.92,
                                     ((img_sdr_srgb_normalized_float + 0.055) / 1.055) ** 2.4)
            sdr_white_nits = 203.0
            img_sRGB_linear_absolute_nits = sdr_linear_display * sdr_white_nits
        
            # Calculate HDR luminance per pixel (BGR order in OpenCV)
            lum_hdr = 0.2126 * img_P3_linear_absolute_nits[:,:,2] + 0.7152 * img_P3_linear_absolute_nits[:,:,1] + 0.0722 * img_P3_linear_absolute_nits[:,:,0]
        
            # Calculate SDR luminance per pixel (BGR order in OpenCV)
            lum_sdr = 0.2126 * img_sRGB_linear_absolute_nits[:,:,2] + 0.7152 * img_sRGB_linear_absolute_nits[:,:,1] + 0.0722 * img_sRGB_linear_absolute_nits[:,:,0]
        
            # Prevent division by zero: replace any values < 1e-6 with 1e-6
            sdr_safe = np.maximum(lum_sdr, 1e-6)
        
            # Calculate gain ratio per pixel: HDR luminance / SDR luminance
            # Result is a 2D array where each element is the gain ratio for that pixel
            gain_ratio = lum_hdr / sdr_safe
        
            # Find the maximum gain ratio across ***ALL pixels***
            # This represents the worst-case gain needed anywhere in the image
            estimated_headroom = np.max(gain_ratio)
            estimated_headroom = max(estimated_headroom, 1.0)
        
            print(f"  Estimated Headroom: {estimated_headroom:.2f} ({np.log2(estimated_headroom):.2f} stops)")

            # Export gain map as PNG for visualization (LUT version only)
            output_dir = os.path.dirname(output_file)
            output_basename = os.path.splitext(os.path.basename(output_file))[0]
            gainmap_png_path = os.path.join(output_dir, f"{output_basename}_gainmap.png")
            export_gain_map_png(img_P3_linear_absolute_nits, img_sRGB_linear_absolute_nits, estimated_headroom, gainmap_png_path)

        else:
            print(f"  ⚠ LUT not found: {lut_filename}.")
            exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

# ============================================================================
# BATCH PROCESSING FUNCTION
# ============================================================================

def process_directory(directory):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(os.path.abspath(directory))
    converted_dir = os.path.join(parent_dir, "converted_gainmap")
    os.makedirs(converted_dir, exist_ok=True)
    
    SUPPORTED_EXTENSIONS = (".tif", ".tiff", ".jpg", ".jpeg", ".png")
    
    try:
        files = os.listdir(directory)
    except PermissionError:
        print(f"✗ Error: Permission denied: {directory}")
        return
    
    image_files = [f for f in files if f.lower().endswith(SUPPORTED_EXTENSIONS)]
    
    if not image_files:
        print(f"⚠ No supported images found in {directory}")
        return
    
    print(f"Found {len(image_files)} images. Generating LUT and Swift versions for each.\n")
    
    for idx, filename in enumerate(image_files, 1):
        file_path = os.path.join(directory, filename)
        base_name = os.path.splitext(filename)[0]
        
        print(f"[{idx}/{len(image_files)}] Processing: {filename}")
        
        output = os.path.join(converted_dir, f"{base_name}.avif")
        if not os.path.exists(output):
            convert_to_avif_gainmap(file_path, output)
        else:
            print("  Skipping (exists)")
        print()


# ============================================================================
# MAIN EXECUTION BLOCK
# ============================================================================

def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {os.path.basename(__file__)} <input_file_or_directory>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    if not os.path.exists(input_path):
        print(f"Error: Path not found: {input_path}")
        sys.exit(1)
    
    # single file conversion
    if os.path.isfile(input_path):
        print(f"\nMode: Single file conversion")
        print(f"Input: {input_path}\n")
        
        input_dir = os.path.dirname(os.path.abspath(input_path))
        parent_dir = os.path.dirname(input_dir)
        converted_dir = os.path.join(parent_dir, "converted_gainmap")
        os.makedirs(converted_dir, exist_ok=True)
        
        # single file conversion
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        
        # LUT Version
        output_lut = os.path.join(converted_dir, f"{base_name}.avif")
        convert_to_avif_gainmap(input_path, output_lut)
        print("\n✓ Done")
    
    # directory conversion 
    elif os.path.isdir(input_path):
        print(f"\nMode: Batch directory processing")
        process_directory(input_path)

def parse_arguments():
    """Parse command-line arguments."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert HDR images to AVIF with adaptive gain maps'
    )
    parser.add_argument(
        'input_path',
        help='Path to HDR image file or directory'
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    main()
