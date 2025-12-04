#!/usr/bin/env swift

/*
 HDR HEIC Gain Map Generator using Core Image
 =============================================
 
 PURPOSE:
 --------
 This Swift script creates HEIC files with adaptive gain maps using
 Apple's Core Image framework. It demonstrates the native macOS/iOS
 approach to HDR image encoding.
 
 CORE IMAGE GAIN MAP:
 --------------------
 When .hdrImage option is provided to writeHEIFRepresentation:
 - Core Image automatically calculates the gain map
 - Gain map = ratio between HDR and SDR representations
 - Encoded using Rec.709 gamma (not linear)
 - Typically scaled to 1/2 resolution for efficiency
 - Embedded as auxiliary image with proper metadata
 
 TWO MODES:
 ----------
 1. External SDR (sdrPath = file path):
    - Uses pre-generated SDR base image (e.g., from LUT)
    - Allows precise control over SDR appearance
    
 2. Internal SDR (sdrPath = "GENERATE"):
    - Core Image generates SDR from HDR automatically
    - Uses Apple's standard tone mapping
    - Best for platform-native compatibility
 
 METADATA:
 ---------
 MakerApple tags are injected for iOS compatibility:
 - Tag 33: HDRHeadroom (ratio value)
 - Tag 48: HDRGain offset (0.0 for standard)
 
 Usage:
    swift convert_hdr_heic.swift <sdr_path|GENERATE> <hdr_path> <output_path> <headroom>
 
 Arguments:
    sdr_path  : Path to SDR image, or "GENERATE" for auto-generation
    hdr_path  : Path to HDR image (should be P3 PQ or Rec.2100 PQ)
    output    : Output HEIC file path
    headroom  : Estimated headroom ratio (e.g., 2.5 for 2.5x)
 
 Requirements:
    - macOS with Core Image framework
    - Swift 5.0+
 */

import Foundation
import CoreImage
import CoreImage.CIFilterBuiltins

// Usage: ./convert_hdr_heic.swift <sdr_path> <hdr_path> <output_path> <headroom>

guard CommandLine.arguments.count >= 5 else {
    print("Usage: ./convert_hdr_heic.swift <sdr_path> <hdr_path> <output_path> <headroom>")
    exit(1)
}

let sdrPath = CommandLine.arguments[1]
let hdrPath = CommandLine.arguments[2]
let outputPath = CommandLine.arguments[3]
let headroom = Double(CommandLine.arguments[4]) ?? 0.0

let hdrURL = URL(fileURLWithPath: hdrPath)
let outputURL = URL(fileURLWithPath: outputPath)

// 1. Load HDR Image (Required for both modes)
guard let hdrImage = CIImage(contentsOf: hdrURL) else {
    print("Error: Could not load HDR image from \(hdrPath)")
    exit(1)
}

var sdrImage: CIImage
var sdrColorSpace: CGColorSpace

if sdrPath == "GENERATE" {
    print("Generating SDR from HDR using Core Image...")
    // Use HDR image as base; Core Image will convert to sRGB during write
    sdrImage = hdrImage
    sdrColorSpace = CGColorSpace(name: CGColorSpace.sRGB)!
} else {
    let sdrURL = URL(fileURLWithPath: sdrPath)
    guard let loadedSdr = CIImage(contentsOf: sdrURL) else {
        print("Error: Could not load SDR image from \(sdrPath)")
        exit(1)
    }
    sdrImage = loadedSdr
    sdrColorSpace = sdrImage.colorSpace ?? CGColorSpace(name: CGColorSpace.sRGB)!
}

// 2. Prepare Metadata with MakerApple Tags
var metadata = sdrImage.properties

// Create or update MakerApple dictionary
var makerApple = metadata[kCGImagePropertyMakerAppleDictionary as String] as? [String: Any] ?? [:]

// Tag 33: HDRHeadroom (ratio value)
makerApple["33"] = headroom

// Tag 48: HDRGain offset (standard value for compatibility)
makerApple["48"] = 0.0

metadata[kCGImagePropertyMakerAppleDictionary as String] = makerApple

// Apply metadata to SDR image
sdrImage = sdrImage.settingProperties(metadata)

// 3. Create Context
// Use ITU-R BT.2100 PQ color space for HDR processing
// This is the standard HDR color space for PQ-encoded content
guard let hdrColorSpace = CGColorSpace(name: CGColorSpace.itur_2100_PQ) else {
    print("Error: Could not create ITU-R BT.2100 PQ color space")
    exit(1)
}

let context = CIContext(options: [.workingColorSpace: hdrColorSpace])

// 4. Set Options for HEIF Export
// The .hdrImage option triggers Core Image's adaptive gain map calculation
// Core Image will automatically:
// - Calculate the gain map from the difference between HDR and SDR
// - Apply proper Rec.709 gamma encoding
// - Scale the gain map appropriately (typically 1/2 resolution)
// - Embed it with the correct auxiliary image type
var options: [CIImageRepresentationOption: Any] = [:]
options[.hdrImage] = hdrImage

// 5. Write HEIF with Adaptive Gain Map
    do {
        try context.writeHEIFRepresentation(of: sdrImage,
                                          to: outputURL,
                                          format: .RGBA8,
                                          colorSpace: sdrColorSpace,
                                          options: options)
        
        print("Successfully created Adaptive HDR HEIC")
        print("  SDR Base: \(sdrPath)")
        print("  HDR Reference: \(hdrPath)")
        print("  Output: \(outputPath)")
        print("  Headroom: \(String(format: "%.2f", headroom)) (\(String(format: "%.2f", log2(headroom))) stops)")
        print("  Method: Core Image Adaptive Gain Map")
        
        exit(0)
    } catch {
        print("Error writing HEIC: \(error)")
        print("  This may indicate:")
        print("  - Invalid input image format")
        print("  - Insufficient permissions")
        print("  - Disk space issues")
        exit(1)
    }

