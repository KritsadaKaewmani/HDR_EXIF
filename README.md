# Python for HDR EXIF learning

Usage

# Activate virtual environment (required for numpy/cv2)

source .venv/bin/activate

# Run script

python3 HDR_EXIF.py <input_file_or_directory>

Key Features

1. Dual ICC Profile Export<br>
Profiles:<br>
✅HDR_P3_D65_ST2084.icc<br>
✅P3_PQ.icc<br>
Method: ImageMagick conversion with embedded profiles<br>
Output: Two HEIC files per input<br>
2. SDR Base Export<br>
Method: Full gain map generation pipeline<br>
Dependencies: numpy, opencv-python, heif-enc, exiftool<br>
Process:<br>
Load 16-bit TIFF<br>
✅Linearize PQ to Nits (using standard ST 2084 EOTF)<br>
✅Generate SDR Base Image (ACES2.0 P3D65PQ1000_to_sRGB22.cube)<br>
✅Calculate Gain Map (HDR Linear / SDR Linear)<br>
✅Stitch Base + Gain Map using heif-enc<br>
✅Inject Apple HDR Headroom metadata<br>
3.Organization<br>
Output: All files saved to converted/ subfolder<br>
Naming: <filename>_<profile_name>.heic<br>

Generated Files in "test_image/converted" folder<br>
filename_HDR_P3_D65_ST2084.heic<br>
filename_P3_PQ.heic<br>
filename_HDR_gain_map.heic<br>

### Reference

<https://developer.apple.com/videos/play/wwdc2023/10181/>
<https://developer.apple.com/documentation/UIKit/supporting-hdr-images-in-your-app>
<https://developer.apple.com/documentation/appkit/applying-apple-hdr-effect-to-your-photos>

## Preview Gallery only : You must load HEIC files from "test_image/converted" folder on your device to see the result

### Image 00

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_00_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_00_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_00_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_00_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 01

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_01_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_01_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_01_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_01_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 02

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_02_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_02_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_02_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_02_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 03

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_03_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_03_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_03_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_03_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 04

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_04_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_04_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_04_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_04_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 05

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_05_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_05_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_05_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_05_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 06

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_06_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_06_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_06_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_06_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 07

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_07_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_07_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_07_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_07_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 08

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_08_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_08_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_08_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_08_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 09

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_09_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_09_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_09_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_09_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 10

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_10_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_10_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_10_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_10_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 11

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_11_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_11_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_11_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_11_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 12

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_12_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_12_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_12_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_12_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 13

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_13_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_13_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_13_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_13_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 14

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_14_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_14_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_14_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_14_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 15

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_15_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_15_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_15_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_15_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 16

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_16_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_16_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_16_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_16_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 17

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_17_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_17_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_17_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_17_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 18

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_18_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_18_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_18_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_18_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 19

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_19_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_19_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_19_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_19_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 20

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_20_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_20_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_20_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_20_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 21

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_21_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_21_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_21_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_21_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 22

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_22_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_22_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_22_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_22_SaveAs_HDR_gain_map_gainmap_full.jpg) |

### Image 23

| P3D65PQ | P3 PQ | SDR Base | Gain Map |
|---|---|---|---|
| ![](test_image/preview/Src_HDR_P3D65PQ_23_SaveAs_HDR_P3_D65_ST2084.png) | ![](test_image/preview/Src_HDR_P3D65PQ_23_SaveAs_P3_PQ.png) | ![](test_image/preview/Src_HDR_P3D65PQ_23_SaveAs_HDR_gain_map.png) | ![](test_image/gainmap/Src_HDR_P3D65PQ_23_SaveAs_HDR_gain_map_gainmap_full.jpg) |
