#!/usr/bin/env python3

"""
HDR HEIC Gain Map Converter
============================

This script converts HDR images to HEIC format with adaptive gain maps
using Apple's Core Image framework via Swift integration.

DUAL-MODE APPROACH:
-------------------
The script generates TWO versions of each HEIC file to compare different
SDR base image generation methods:

1. **LUT Mode** (_LUT.heic):
   - Uses ACES 2.0 LUT (ACES20_P3D65PQ1000D60_to_sRGBPW.cube)
   - Provides precise, cinematically-graded SDR base image
   - Best for maintaining specific color science workflows
   
2. **Swift Mode** (_Swift.heic):
   - Uses Apple's Core Image automatic SDR generation
   - Leverages native macOS/iOS tone mapping algorithms
   - Best for platform-native HDR display compatibility

COLOR MANAGEMENT:
-----------------
All input images are normalized to P3 D65 PQ (ST.2084) color space
using ImageMagick before processing. This ensures:
- Consistent input regardless of source profile
- Correct LUT application (LUT expects P3 PQ input)
- Proper gain map calculation

GAIN MAP VISUALIZATION:
-----------------------
For each HEIC file, a corresponding PNG gain map is exported:
- Filename: <source>_<mode>_gainmap.png
- Content: Grayscale visualization of HDR/SDR ratio
- Normalization: (gain - 1.0) / (max_headroom - 1.0)
- Enhancement: Gamma 0.5 + 3x boost for visibility
- Purpose: Study and compare gain map distributions

WORKFLOW:
---------
1. Convert input to P3 PQ using ImageMagick
2. Load as 16-bit linear data (PQ EOTF applied)
3. Generate SDR base (LUT or fallback tone mapping)
4. Calculate gain map in Python (HDR / SDR ratio)
5. Save gain map PNG for study
6. Call Swift script to create HEIC with Core Image
7. Inject Apple HDR metadata using ExifTool

Usage:
    python HDR_GainMap.py <input_file_or_directory>

Requirements:
    - Python 3.x with numpy, opencv-python, scipy
    - Swift compiler (for Core Image integration)
    - ImageMagick (for color space conversion)
    - ExifTool (for metadata injection)
    - ACES LUT file: ACES20_P3D65PQ1000D60_to_sRGBPW.cube
    - ICC Profile: HDR_P3_D65_ST2084.icc

Output:
    - converted_gainmap/<filename>_LUT.heic
    - converted_gainmap/<filename>_LUT_gainmap.png
    - converted_gainmap/<filename>_Swift.heic
    - converted_gainmap/<filename>_Swift_gainmap.png
"""

# ============================================================================
# IMPORTS
# ============================================================================

import os
import subprocess
import sys
import numpy as np
import cv2
from scipy.interpolate import RegularGridInterpolator


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def pq_eotf(image_pq):
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

def linear_to_srgb(linear_image):
    """
    Simple tone mapping and gamma correction for the SDR Base Image.
    Used as fallback if LUT is missing.
    """
    # 1. Simple Tone Mapping (Reinhard or similar) to bring 1000 nits down to 0-1
    sdr_white_nits = 203.0 
    mapped = linear_image / sdr_white_nits
    mapped = mapped / (1 + mapped) # Reinhard tonemap
    
    # 2. Gamma Correct (Standard sRGB approx)
    srgb = np.where(mapped <= 0.0031308, 
                    12.92 * mapped, 
                    1.055 * (mapped ** (1.0/2.4)) - 0.055)
    return np.clip(srgb, 0, 1)

def convert_to_p3_pq(input_file, output_file):
    """
    Converts input image to P3 D65 PQ (ST.2084) 16-bit TIFF.
    This ensures consistent input for LUT application and Swift processing,
    handling source color profiles correctly.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_profile = os.path.join(script_dir, "HDR_P3_D65_ST2084.icc")
    
    if not os.path.exists(target_profile):
        raise FileNotFoundError(f"Required ICC profile not found: {target_profile}")
        
    cmd = [
        "/opt/homebrew/bin/magick",
        input_file,
        "-depth", "16",
        "-profile", target_profile,
        output_file
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error converting to P3 PQ: {e.stderr}")
        raise


# ============================================================================
# GAIN MAP CONVERSION FUNCTION
# ============================================================================

def convert_to_heif_gainmap(input_file, output_file, mode='lut'):
    """
    Convert HDR image to HEIC with an embedded Gain Map using Core Image.
    
    Parameters:
        input_file (str): Path to the HDR source image
        output_file (str): Path where the HEIC file will be saved
        mode (str): 'lut' (use ACES LUT for SDR) or 'swift' (Core Image auto SDR)
    """
    temp_p3_pq = f"temp_p3_pq_{os.getpid()}.tif"
    temp_sdr = f"temp_sdr_{os.getpid()}.jpg"
    
    try:
        print(f"  Preparing HDR input (converting to P3 PQ)...")
        convert_to_p3_pq(input_file, temp_p3_pq)
        
        # 1. Load HDR Image for statistics (from the converted P3 PQ file)
        img_uq = cv2.imread(temp_p3_pq, cv2.IMREAD_UNCHANGED)
        if img_uq is None:
            raise ValueError(f"Could not read converted image: {temp_p3_pq}")
            
        # Convert to 0-1 Float PQ
        img_pq = img_uq.astype(np.float32) / 65535.0

        # Linearize PQ to Nits for statistics and headroom calc
        img_linear = pq_eotf(img_pq)
        
        # Calculate stats
        hdr_max_nits = np.max(img_linear)
        print(f"  HDR Max Nits: {hdr_max_nits:.2f}")
        
        # Calculate Headroom
        # We estimate this to inject into metadata.
        # For 'swift' mode, we still need this for the MakerApple tags.
        
        # Create a simple SDR approximation for headroom calculation if in 'swift' mode,
        # or use the actual SDR if in 'lut' mode.
        
        sdr_arg = "GENERATE"
        
        if mode == 'lut':
            # --- LUT Mode: Generate SDR using ACES LUT ---
            lut_filename = "ACES20_P3D65PQ1000D60_to_sRGBPW.cube"
            script_dir = os.path.dirname(os.path.abspath(__file__))
            lut_path = os.path.join(script_dir, lut_filename)
            
            if os.path.exists(lut_path):
                print(f"  Applying LUT for SDR base: {lut_filename}")
                lut_3d = read_cube_lut(lut_path)
                
                # Convert BGR to RGB for LUT application
                img_pq_rgb = cv2.cvtColor(img_pq, cv2.COLOR_BGR2RGB)
                
                # Apply LUT
                img_sdr_srgb_rgb = apply_lut(img_pq_rgb, lut_3d)
                img_sdr_srgb = img_sdr_srgb_rgb.astype(np.float32)
                img_sdr_srgb = np.clip(img_sdr_srgb, 0, 1)
            else:
                print(f"  ⚠ LUT not found: {lut_filename}. Using fallback.")
                img_sdr_srgb = linear_to_srgb(img_linear.copy())
            
            # Save SDR temp file
            img_sdr_uint8 = (img_sdr_srgb * 255).astype(np.uint8)
            # Convert back to BGR for saving
            img_sdr_bgr = cv2.cvtColor(img_sdr_uint8, cv2.COLOR_RGB2BGR)
            cv2.imwrite(temp_sdr, img_sdr_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
            sdr_arg = temp_sdr
            
            # Use this SDR for headroom calc
            sdr_norm = img_sdr_srgb
            
        else:
            # --- Swift Mode: Let Core Image generate SDR ---
            print(f"  Mode: Pure Swift (Core Image SDR generation)")
            sdr_arg = "GENERATE"
            
            # For headroom estimation, we simulate a standard SDR render
            # or just use a safe default if we trust Core Image?
            # Better to estimate it from the HDR data assuming standard mapping.
            sdr_norm = linear_to_srgb(img_linear.copy())

        # Calculate Headroom
        sdr_linear_display = np.where(sdr_norm <= 0.04045,
                                     sdr_norm / 12.92,
                                     ((sdr_norm + 0.055) / 1.055) ** 2.4)
        sdr_white_nits = 203.0
        img_sdr_linear = sdr_linear_display * sdr_white_nits
        
        lum_hdr = 0.2126 * img_linear[:,:,2] + 0.7152 * img_linear[:,:,1] + 0.0722 * img_linear[:,:,0]
        lum_sdr = 0.2126 * img_sdr_linear[:,:,2] + 0.7152 * img_sdr_linear[:,:,1] + 0.0722 * img_sdr_linear[:,:,0]
        
        sdr_safe = np.maximum(lum_sdr, 1e-6)
        gain_ratio = lum_hdr / sdr_safe
        estimated_headroom = np.max(gain_ratio)
        estimated_headroom = max(estimated_headroom, 1.0)
        
        print(f"  Estimated Headroom: {estimated_headroom:.2f} ({np.log2(estimated_headroom):.2f} stops)")

        # 3. Calculate and save gain map as PNG (before calling Swift)
        output_dir = os.path.dirname(output_file)
        output_basename = os.path.splitext(os.path.basename(output_file))[0]
        gainmap_png_path = os.path.join(output_dir, f"{output_basename}_gainmap.png")
        
        print(f"  Calculating gain map...")
        # Calculate gain ratio per pixel: HDR / SDR
        # Avoid division by zero
        img_sdr_linear_safe = np.maximum(img_sdr_linear, 1e-6)
        gain_map = img_linear / img_sdr_linear_safe
        
        # Clamp to reasonable range [1.0, estimated_headroom]
        gain_map = np.clip(gain_map, 1.0, estimated_headroom)
        
        # Normalize to 0-1 range for visualization
        # (gain - 1.0) / (max_gain - 1.0)
        gain_map_normalized = (gain_map - 1.0) / max(estimated_headroom - 1.0, 0.01)
        
        # Apply gamma for better visualization (similar to log)
        gain_map_gamma = np.power(gain_map_normalized, 0.5)
        
        # Boost for visibility
        gain_map_boosted = gain_map_gamma * 3.0
        gain_map_boosted = np.clip(gain_map_boosted, 0, 1)
        
        # Convert to 8-bit and save
        gain_map_uint8 = (gain_map_boosted * 255).astype(np.uint8)
        # Convert RGB to BGR for cv2
        gain_map_bgr = cv2.cvtColor(gain_map_uint8, cv2.COLOR_RGB2BGR)
        cv2.imwrite(gainmap_png_path, gain_map_bgr)
        print(f"  ✓ Gain map saved: {gainmap_png_path}")

        # 4. Call Swift script (without gain map generation)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        swift_script = os.path.join(script_dir, "convert_hdr_heic.swift")
        
        cmd = [
            "swift",
            swift_script,
            sdr_arg,           # SDR path or "GENERATE"
            temp_p3_pq,        # HDR image (P3 PQ)
            output_file,       # Output HEIC path
            str(estimated_headroom)
            # Note: removed gainmap_png_path - we generate it in Python now
        ]
        
        print(f"  Running Swift conversion...")
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"{result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Swift conversion failed: {e.stderr}")
            raise e
        
        # 4. Inject Metadata via ExifTool
        headroom_stops = np.log2(estimated_headroom) if estimated_headroom > 1.0 else 0.0
        
        subprocess.run([
            "exiftool", 
            "-overwrite_original",
            f"-XMP:HDRGainMapVersion=65536",
            f"-Apple:HDRHeadroom={headroom_stops:.4f}",
            f"-Apple:HDRGainMapVersion=65536",
            f"-Apple:HDRGainMapMin=0.0",
            f"-Apple:HDRGainMapMax={estimated_headroom:.4f}",
            f"-MakerApple:33=0.8", # Fallback
            f"-MakerApple:48=0.0",
            output_file
        ], check=False, capture_output=True, text=True)
        
        print(f"✓ Created {os.path.basename(output_file)}")

    except Exception as e:
        print(f"✗ Error: {e}")
        raise
    finally:
        # Cleanup
        if os.path.exists(temp_p3_pq): os.remove(temp_p3_pq)
        if os.path.exists(temp_sdr): os.remove(temp_sdr)


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
        
        # Version 1: LUT
        output_lut = os.path.join(converted_dir, f"{base_name}_LUT.heic")
        if not os.path.exists(output_lut):
            print("  Generating LUT version...")
            try:
                convert_to_heif_gainmap(file_path, output_lut, mode='lut')
            except Exception:
                pass
        else:
            print("  Skipping LUT version (exists)")
            
        # Version 2: Swift
        output_swift = os.path.join(converted_dir, f"{base_name}_Swift.heic")
        if not os.path.exists(output_swift):
            print("  Generating Swift version...")
            try:
                convert_to_heif_gainmap(file_path, output_swift, mode='swift')
            except Exception:
                pass
        else:
            print("  Skipping Swift version (exists)")
            
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
        
    if os.path.isfile(input_path):
        print(f"\nMode: Single file conversion")
        print(f"Input: {input_path}\n")
        
        input_dir = os.path.dirname(os.path.abspath(input_path))
        parent_dir = os.path.dirname(input_dir)
        converted_dir = os.path.join(parent_dir, "converted_gainmap")
        os.makedirs(converted_dir, exist_ok=True)
        
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        
        # LUT Version
        output_lut = os.path.join(converted_dir, f"{base_name}_LUT.heic")
        print("Generating LUT version...")
        convert_to_heif_gainmap(input_path, output_lut, mode='lut')
        
        # Swift Version
        output_swift = os.path.join(converted_dir, f"{base_name}_Swift.heic")
        print("\nGenerating Swift version...")
        convert_to_heif_gainmap(input_path, output_swift, mode='swift')
        
        print("\n✓ Done")
        
    elif os.path.isdir(input_path):
        print(f"\nMode: Batch directory processing")
        process_directory(input_path)

if __name__ == "__main__":
    main()
