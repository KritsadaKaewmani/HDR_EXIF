# HDR HEIC Conversion Toolkit

Educational playground for learning HDR image processing, ICC profile management, and Apple gain map generation.

## 📚 Purpose

This project demonstrates two distinct approaches to HDR HEIC conversion:

1. **Simple ICC Profile Embedding** (`HDR_ICC.py`)
   - Educational tool for understanding ICC profile workflows
   - Preserves pixel values while changing color space tags

2. **Adaptive Gain Map Generation** (`HDR_GainMap.py`)
   - Demonstrates Apple's HDR gain map technology
   - Compares LUT-based vs. Core Image SDR generation

## 🛠️ Scripts

### HDR_ICC.py

Simple HEIC conversion with ICC profile embedding.

**Purpose**: Learn how ICC profiles work without color conversion

**Strategy**: "Preserve Pixels"

- Strip existing profile
- Embed target profile
- No pixel value changes

**Usage**:

```bash
python HDR_ICC.py <input_file_or_directory>
python HDR_ICC.py -o <input>  # Overwrite existing files
```

**Output**: `converted_with_ICC/Src_<filename>_SaveAs_<profile>.heic`

### HDR_GainMap.py

Advanced HEIC conversion with adaptive gain maps.

**Purpose**: Learn Apple's HDR gain map technology

**Dual-Mode Approach**:

- **LUT Mode**: Uses ACES 2.0 LUT for cinematically-graded SDR
- **Swift Mode**: Uses Core Image's native tone mapping

**Features**:

- Automatic P3 PQ color space normalization
- Gain map PNG export for study
- Dual HEIC output for comparison

**Usage**:

```bash
python HDR_GainMap.py <input_file_or_directory>
```

**Output**:

```
converted_gainmap/
├── <filename>_LUT.heic          # LUT-based SDR
├── <filename>_LUT_gainmap.png   # Gain map visualization
├── <filename>_Swift.heic        # Core Image SDR
└── <filename>_Swift_gainmap.png # Gain map visualization
```

### convert_hdr_heic.swift

Core Image integration for native macOS/iOS gain map generation.

**Purpose**: Demonstrate Apple's native HDR encoding

**Modes**:

- External SDR: Use pre-generated SDR base
- Internal SDR: Auto-generate from HDR

**Usage**:

```bash
swift convert_hdr_heic.swift <sdr_path|GENERATE> <hdr_path> <output> <headroom>
```

## 📋 Requirements

### Python Dependencies

```bash
pip install numpy opencv-python scipy
```

### System Tools

- **ImageMagick 7+**: `/opt/homebrew/bin/magick`
- **ExifTool**: For metadata injection
- **Swift 5.0+**: For Core Image integration

### Required Files

- `HDR_P3_D65_ST2084.icc` - Display P3 PQ profile
- `P3_PQ.icc` - Alternative P3 PQ profile
- `ACES20_P3D65PQ1000D60_to_sRGBPW.cube` - ACES 2.0 LUT

## 🎓 Learning Concepts

### 1. ICC Profile Management

- Profile embedding vs. color conversion
- "Preserve pixels" strategy
- Avoiding unwanted tone mapping

### 2. Color Space Workflows

- P3 D65 PQ (ST.2084) normalization
- LUT application requirements
- Consistent input handling

### 3. HDR Gain Maps

- Ratio-based encoding (HDR / SDR)
- Gamma vs. linear encoding
- Visualization techniques

### 4. Apple HDR Technology

- Core Image automatic gain map calculation
- MakerApple metadata tags
- Platform-native compatibility

## 📊 Gain Map Visualization

Exported PNG gain maps show:

- **Grayscale representation** of HDR/SDR ratio
- **Normalized range**: (gain - 1.0) / (max_headroom - 1.0)
- **Enhanced visibility**: Gamma 0.5 + 3x boost
- **Purpose**: Study and compare gain map distributions

Interpretation:

- **Darker areas**: Low gain (SDR ≈ HDR)
- **Brighter areas**: High gain (significant HDR boost)

## 🔄 Typical Workflow

### For Learning ICC Profiles

```bash
# Simple profile embedding
python HDR_ICC.py test_image/src/

# Check results
ls converted_with_ICC/
```

### For Learning Gain Maps

```bash
# Generate dual-mode HEIC files
python HDR_GainMap.py test_image/src/

# Study gain maps
open converted_gainmap/*_gainmap.png

# Compare HEIC files on iOS/macOS device
```

## 📁 Project Structure

```
HDR_EXIF/
├── HDR_ICC.py                              # ICC profile embedding
├── HDR_GainMap.py                          # Gain map generation
├── convert_hdr_heic.swift                  # Core Image integration
├── HDR_P3_D65_ST2084.icc                   # ICC profile
├── P3_PQ.icc                               # ICC profile
├── ACES20_P3D65PQ1000D60_to_sRGBPW.cube   # ACES LUT
├── test_image/                             # Test images
│   ├── src/                                # Source HDR images
│   ├── converted_with_ICC/                 # ICC profile outputs
│   └── converted_gainmap/                  # Gain map outputs
└── README.md
```

## ⚠️ Important Notes

1. **Educational Purpose**: This is a learning playground, not production code
2. **Color Accuracy**: Results depend on source profile accuracy
3. **Platform Testing**: Test HEIC files on actual iOS/macOS devices
4. **LUT Requirements**: ACES LUT expects P3 PQ input (handled automatically)

## 🔗 References

- [WWDC 2023: Support HDR images in your app](https://developer.apple.com/videos/play/wwdc2023/10181/)
- [UIKit: Supporting HDR images](https://developer.apple.com/documentation/UIKit/supporting-hdr-images-in-your-app)
- [AppKit: Applying Apple HDR Effect](https://developer.apple.com/documentation/appkit/applying-apple-hdr-effect-to-your-photos)
- [SMPTE ST 2084: PQ EOTF](https://ieeexplore.ieee.org/document/7291452)

## 📝 License

Educational use only. See individual file headers for details.
