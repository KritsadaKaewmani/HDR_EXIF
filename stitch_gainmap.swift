#!/usr/bin/env swift

import Foundation
import ImageIO
import UniformTypeIdentifiers

// Usage: ./stitch_gainmap.swift <sdr_path> <gainmap_path> <output_path> <headroom>

guard CommandLine.arguments.count >= 5 else {
    print("Usage: ./stitch_gainmap.swift <sdr_path> <gainmap_path> <output_path> <headroom>")
    exit(1)
}

let sdrPath = CommandLine.arguments[1]
let gainMapPath = CommandLine.arguments[2]
let outputPath = CommandLine.arguments[3]
let headroom = Double(CommandLine.arguments[4]) ?? 0.0

let sdrURL = URL(fileURLWithPath: sdrPath)
let gainMapURL = URL(fileURLWithPath: gainMapPath)
let outputURL = URL(fileURLWithPath: outputPath)

// 1. Load SDR Image
guard let sdrSource = CGImageSourceCreateWithURL(sdrURL as CFURL, nil),
      let sdrImage = CGImageSourceCreateImageAtIndex(sdrSource, 0, nil) else {
    print("Error: Could not load SDR image")
    exit(1)
}

// 2. Load Gain Map Image
guard let gainMapSource = CGImageSourceCreateWithURL(gainMapURL as CFURL, nil),
      let gainMapImage = CGImageSourceCreateImageAtIndex(gainMapSource, 0, nil) else {
    print("Error: Could not load Gain Map image")
    exit(1)
}

// 3. Prepare Metadata
// Get existing metadata from SDR image
var metadata = CGImageSourceCopyPropertiesAtIndex(sdrSource, 0, nil) as? [String: Any] ?? [:]
var exifDictionary = metadata[kCGImagePropertyExifDictionary as String] as? [String: Any] ?? [:]
var makerAppleDictionary = metadata[kCGImagePropertyMakerAppleDictionary as String] as? [String: Any] ?? [:]
var xmpDictionary = metadata[kCGImagePropertyXML as String] as? [String: Any] ?? [:]

// Calculate headroom stops
let headroomStops = log2(max(headroom, 1.0))

// Set Apple HDR Metadata
// Note: We set these in the MakerApple dictionary for older iOS compatibility
// and also as top-level keys if supported.
makerAppleDictionary["33"] = 0.8
makerAppleDictionary["48"] = 0.0

// Update metadata dictionaries
metadata[kCGImagePropertyMakerAppleDictionary as String] = makerAppleDictionary

// 4. Create Destination
guard let destination = CGImageDestinationCreateWithURL(outputURL as CFURL, UTType.heic.identifier as CFString, 1, nil) else {
    print("Error: Could not create output destination")
    exit(1)
}

// 5. Add Gain Map as Auxiliary Image
// Apple uses kCGImageAuxiliaryDataTypeHDRGainMap (urn:com:apple:photo:2020:aux:hdrgainmap)
let auxDataType = kCGImageAuxiliaryDataTypeHDRGainMap

// Create auxiliary data dictionary
let auxAttributes: [String: Any] = [
    kCGImageAuxiliaryDataInfoData as String: gainMapImage, // Pass the CGImage directly? No, usually Data or CVPixelBuffer.
                                                           // ImageIO expects the image data or a CGImage in some contexts.
                                                           // Let's try adding it as a separate image with the auxiliary tag?
                                                           // Actually, CGImageDestinationAddAuxiliaryDataInfo is the API.
]

// Wait, CGImageDestinationAddAuxiliaryDataInfo is for adding aux data *to* an image being added.
// But we need to construct the aux info dictionary correctly.

// Let's try a simpler approach:
// Use CGImageDestinationAddImageAndMetadata, but we need to attach the aux image.

// Correct approach for ImageIO:
// 1. Create a dictionary for the auxiliary image
// 2. The dictionary must contain the data (CFData) and description (width, height, etc.)

// Convert Gain Map CGImage to Data (HEVC or JPEG encoded inside the aux data? Or raw pixels?)
// Apple's format usually expects the aux image to be compressed (e.g. JPEG/HEVC) stored as data.

// 5. Prepare Gain Map Data (L8 Format)
let width = CGImageGetWidth(gainMapImage)
let height = CGImageGetHeight(gainMapImage)
let bytesPerRow = width // 1 byte per pixel for L8
let bitmapByteCount = bytesPerRow * height

// Create L8 Context
var rawData = [UInt8](repeating: 0, count: bitmapByteCount)
guard let context = CGContext(data: &rawData,
                              width: width,
                              height: height,
                              bitsPerComponent: 8,
                              bytesPerRow: bytesPerRow,
                              space: CGColorSpaceCreateDeviceGray(),
                              bitmapInfo: CGImageAlphaInfo.none.rawValue) else {
    print("Error: Could not create L8 context")
    exit(1)
}

// Draw gain map into context
let rect = CGRect(x: 0, y: 0, width: Double(width), height: Double(height))
context.draw(gainMapImage, in: rect)

// Get data from context
let gainMapData = Data(bytes: rawData, count: bitmapByteCount)

// 6. Create Auxiliary Info Dictionary
let auxInfo: [String: Any] = [
    kCGImageAuxiliaryDataInfoData as String: gainMapData as CFData,
    kCGImageAuxiliaryDataInfoDataDescription as String: [
        kCGImagePropertyPixelWidth as String: width,
        kCGImagePropertyPixelHeight as String: height,
        kCGImagePropertyBytesPerRow as String: bytesPerRow,
        kCGImagePropertyColorModel as String: kCGImagePropertyColorModelGray
    ]
]

// 7. Add Image with Auxiliary Data
CGImageDestinationAddImage(destination, sdrImage, metadata as CFDictionary)
CGImageDestinationAddAuxiliaryDataInfo(destination, auxDataType, auxInfo as CFDictionary)

// 8. Finalize
if CGImageDestinationFinalize(destination) {
    print("Successfully created HEIC with Gain Map")
    exit(0)
} else {
    print("Error: Could not finalize destination")
    exit(1)
}
