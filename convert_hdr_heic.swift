#!/usr/bin/env swift

import Foundation
import CoreImage
import CoreImage.CIFilterBuiltins

// Usage: ./convert_hdr_heic.swift <sdr_path> <hdr_path> <output_path>

guard CommandLine.arguments.count >= 5 else {
    print("Usage: ./convert_hdr_heic.swift <sdr_path> <hdr_path> <output_path> <headroom>")
    exit(1)
}

let sdrPath = CommandLine.arguments[1]
let hdrPath = CommandLine.arguments[2]
let outputPath = CommandLine.arguments[3]
let headroom = Double(CommandLine.arguments[4]) ?? 0.0

let sdrURL = URL(fileURLWithPath: sdrPath)
let hdrURL = URL(fileURLWithPath: hdrPath)
let outputURL = URL(fileURLWithPath: outputPath)

// 1. Load Images
guard let sdrImageOriginal = CIImage(contentsOf: sdrURL) else {
    print("Error: Could not load SDR image from \(sdrPath)")
    exit(1)
}

guard let hdrImage = CIImage(contentsOf: hdrURL) else {
    print("Error: Could not load HDR image from \(hdrPath)")
    exit(1)
}

// 2. Prepare Metadata with MakerApple Tags
// We need to inject the Apple-specific metadata that Core Image might not set automatically
// or that we want to ensure matches the reference.
var metadata = sdrImageOriginal.properties

// Create or update MakerApple dictionary
var makerApple = metadata[kCGImagePropertyMakerAppleDictionary as String] as? [String: Any] ?? [:]

// Tag 33: HDRHeadroom (usually the ratio or stops, let's use the passed headroom ratio)
// Reference file had 1.1979. Our calculated headroom is passed in.
makerApple["33"] = headroom

// Tag 48: HDRGain (often related to min/max or offset)
// Reference file had 0.1718. Previous examples used 0.0.
// Let's set it to 0.0 for now as a safe default, or we could calculate it if we knew the formula.
makerApple["48"] = 0.0

metadata[kCGImagePropertyMakerAppleDictionary as String] = makerApple

// Apply metadata to SDR image
let sdrImage = sdrImageOriginal.settingProperties(metadata)

// 3. Create Context
// We use a context that supports working with HDR color spaces
let context = CIContext(options: [.workingColorSpace: CGColorSpace(name: CGColorSpace.itur_2100_PQ)!])

// 4. Set Options for HEIF Export
// The key .hdrImage is what triggers the gain map calculation
var options: [CIImageRepresentationOption: Any] = [:]
options[.hdrImage] = hdrImage

// 5. Write HEIF
do {
    try context.writeHEIFRepresentation(of: sdrImage,
                                      to: outputURL,
                                      format: .RGBA8,
                                      colorSpace: sdrImage.colorSpace ?? CGColorSpace(name: CGColorSpace.sRGB)!,
                                      options: options)
    
    print("Successfully created Adaptive HDR HEIC at \(outputPath)")
    exit(0)
} catch {
    print("Error writing HEIC: \(error)")
    exit(1)
}
