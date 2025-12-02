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

![](test_image/preview/Src_HDR_P3D65PQ_00_SaveAs_HDR_P3_D65_ST2084.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_00_SaveAs_P3_PQ.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_00_SaveAs_HDR_gain_map.png) <br>
![](test_image/gainmap/Src_HDR_P3D65PQ_00_SaveAs_HDR_gain_map_gainmap_full.jpg) <br>

### Image 01

![](test_image/preview/Src_HDR_P3D65PQ_01_SaveAs_HDR_P3_D65_ST2084.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_01_SaveAs_P3_PQ.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_01_SaveAs_HDR_gain_map.png) <br>
![](test_image/gainmap/Src_HDR_P3D65PQ_01_SaveAs_HDR_gain_map_gainmap_full.jpg) <br>

### Image 03

![](test_image/preview/Src_HDR_P3D65PQ_03_SaveAs_HDR_P3_D65_ST2084.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_03_SaveAs_P3_PQ.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_03_SaveAs_HDR_gain_map.png) <br>
![](test_image/gainmap/Src_HDR_P3D65PQ_03_SaveAs_HDR_gain_map_gainmap_full.jpg) <br>

### Image 04

![](test_image/preview/Src_HDR_P3D65PQ_04_SaveAs_HDR_P3_D65_ST2084.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_04_SaveAs_P3_PQ.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_04_SaveAs_HDR_gain_map.png) <br>
![](test_image/gainmap/Src_HDR_P3D65PQ_04_SaveAs_HDR_gain_map_gainmap_full.jpg) <br>

### Image 06

![](test_image/preview/Src_HDR_P3D65PQ_06_SaveAs_HDR_P3_D65_ST2084.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_06_SaveAs_P3_PQ.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_06_SaveAs_HDR_gain_map.png) <br>
![](test_image/gainmap/Src_HDR_P3D65PQ_06_SaveAs_HDR_gain_map_gainmap_full.jpg) <br>

### Image 08

![](test_image/preview/Src_HDR_P3D65PQ_08_SaveAs_HDR_P3_D65_ST2084.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_08_SaveAs_P3_PQ.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_08_SaveAs_HDR_gain_map.png) <br>
![](test_image/gainmap/Src_HDR_P3D65PQ_08_SaveAs_HDR_gain_map_gainmap_full.jpg) <br>

### Image 09

![](test_image/preview/Src_HDR_P3D65PQ_09_SaveAs_HDR_P3_D65_ST2084.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_09_SaveAs_P3_PQ.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_09_SaveAs_HDR_gain_map.png) <br>
![](test_image/gainmap/Src_HDR_P3D65PQ_09_SaveAs_HDR_gain_map_gainmap_full.jpg) <br>

### Image 11

![](test_image/preview/Src_HDR_P3D65PQ_11_SaveAs_HDR_P3_D65_ST2084.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_11_SaveAs_P3_PQ.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_11_SaveAs_HDR_gain_map.png) <br>
![](test_image/gainmap/Src_HDR_P3D65PQ_11_SaveAs_HDR_gain_map_gainmap_full.jpg) <br>

### Image 12

![](test_image/preview/Src_HDR_P3D65PQ_12_SaveAs_HDR_P3_D65_ST2084.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_12_SaveAs_P3_PQ.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_12_SaveAs_HDR_gain_map.png) <br>
![](test_image/gainmap/Src_HDR_P3D65PQ_12_SaveAs_HDR_gain_map_gainmap_full.jpg) <br>

### Image 13

![](test_image/preview/Src_HDR_P3D65PQ_13_SaveAs_HDR_P3_D65_ST2084.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_13_SaveAs_P3_PQ.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_13_SaveAs_HDR_gain_map.png) <br>
![](test_image/gainmap/Src_HDR_P3D65PQ_13_SaveAs_HDR_gain_map_gainmap_full.jpg) <br>

### Image 15

![](test_image/preview/Src_HDR_P3D65PQ_15_SaveAs_HDR_P3_D65_ST2084.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_15_SaveAs_P3_PQ.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_15_SaveAs_HDR_gain_map.png) <br>
![](test_image/gainmap/Src_HDR_P3D65PQ_15_SaveAs_HDR_gain_map_gainmap_full.jpg) <br>

### Image 21

![](test_image/preview/Src_HDR_P3D65PQ_21_SaveAs_HDR_P3_D65_ST2084.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_21_SaveAs_P3_PQ.png) <br>
![](test_image/preview/Src_HDR_P3D65PQ_21_SaveAs_HDR_gain_map.png) <br>
![](test_image/gainmap/Src_HDR_P3D65PQ_21_SaveAs_HDR_gain_map_gainmap_full.jpg) <br>
