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
Generate SDR Base Image (ACES2.0 P3D65PQ1000_to_sRGB22.cube)
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

Generated Files
filename_HDR_P3_D65_ST2084.heic
filename_P3_PQ.heic
filename_HDR_gain_map.heic

## Preview Gallery only you must load HEIC on your device to see the result

### Image 00

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_00_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_00_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_00_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_00_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 01

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_01_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_01_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_01_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_01_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 02

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_02_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_02_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_02_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_02_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 03

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_03_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_03_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_03_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_03_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 04

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_04_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_04_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_04_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_04_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 05

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_05_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_05_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_05_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_05_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 06

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_06_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_06_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_06_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_06_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 07

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_07_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_07_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_07_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_07_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 08

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_08_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_08_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_08_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_08_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 09

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_09_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_09_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_09_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_09_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 10

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_10_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_10_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_10_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_10_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 11

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_11_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_11_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_11_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_11_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 12

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_12_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_12_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_12_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_12_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 13

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_13_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_13_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_13_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_13_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 14

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_14_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_14_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_14_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_14_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 15

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_15_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_15_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_15_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_15_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 16

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_16_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_16_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_16_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_16_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 17

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_17_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_17_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_17_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_17_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 18

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_18_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_18_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_18_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_18_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 19

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_19_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_19_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_19_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_19_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 20

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_20_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_20_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_20_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_20_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 21

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_21_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_21_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_21_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_21_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 22

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_22_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_22_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_22_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_22_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 23

| HDR P3 D65 ST2084 | P3 PQ | HDR Gain Map | Gain Map Visualization |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_23_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_23_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_23_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_23_SaveAs_HDR_gain_map_gainmap_full.jpg) |

Usage

# Activate virtual environment (required for numpy/cv2)

source .venv/bin/activate

# Run script

python3 HDR_EXIF.py <input_file_or_directory>
