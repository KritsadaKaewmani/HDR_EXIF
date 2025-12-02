# Python for HDR EXIF learning

HDR_EXIF.py Modifications
Overview
Modified
HDR_EXIF.py
 to implement a robust HDR workflow with three export options, including a true HDR gain map implementation.

Key Features

1. Dual ICC Profile Export
Profiles:
HDR_P3_D65_ST2084.icc
 and
P3_PQ.icc
Method: ImageMagick conversion with embedded profiles
Output: Two HEIC files per input
2. HDR Gain Map Export
Method: Full gain map generation pipeline
Dependencies: numpy, opencv-python, heif-enc, exiftool
Process:
Load 16-bit TIFF
Linearize PQ to Nits (using standard ST 2084 EOTF)
Generate SDR Base Image (Tone mapping + sRGB Gamma)
Calculate Gain Map (HDR Linear / SDR Linear)
Stitch Base + Gain Map using heif-enc
Inject Apple HDR Headroom metadata
3. Text Overlay
Style: Arial font, 15px size, Gray 0.5 text on Black highlight
Content: Displays the profile name (e.g., "HDR_gain_map")
Applied to: All three export versions
4. Organization
Output: All files saved to converted/ subfolder
Naming: <filename>_<profile_name>.heic
Verification Results
Tested with HDR_P3D65PQ1000nits.00000000.tif:

Generated Files
HDR_P3D65PQ1000nits.00000000_HDR_P3_D65_ST2084.heic
HDR_P3D65PQ1000nits.00000000_P3_PQ.heic
HDR_P3D65PQ1000nits.00000000_HDR_gain_map.heic
Gain Map Validation
Headroom Calculation: 2.14 (1.10 stops) for the test image
Text Overlay: Verified "HDR_gain_map" label on the base image
Structure: Valid HEIC with auxiliary image
Usage

# Activate virtual environment (required for numpy/cv2)

source .venv/bin/activate

# Run script

python3 HDR_EXIF.py <input_file_or_directory>
