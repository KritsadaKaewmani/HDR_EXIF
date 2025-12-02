#!/usr/bin/env python3
"""
PNG Preview Generator for README.md
====================================

This script converts all HEIC files from the converted folder to PNG format
for use in the README.md preview gallery.

Usage:
    python3 gen_png_preview.py

Requirements:
    - ImageMagick 7+ installed at /opt/homebrew/bin/magick
"""

import os
import subprocess
import sys
from pathlib import Path


def convert_heic_to_png(heic_file, png_file):
    """
    Convert a single HEIC file to PNG using ImageMagick.
    
    Parameters:
        heic_file (str): Path to source HEIC file
        png_file (str): Path to output PNG file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cmd = [
            "/opt/homebrew/bin/magick",
            heic_file,
            png_file
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error converting {os.path.basename(heic_file)}: {e.stderr}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def main():
    """
    Main function to batch convert all HEIC files to PNG.
    """
    # Get script directory
    script_dir = Path(__file__).parent.absolute()
    
    # Define paths
    converted_dir = script_dir / "test_image" / "converted"
    preview_dir = script_dir / "test_image" / "preview"
    
    # Validate directories
    if not converted_dir.exists():
        print(f"✗ Error: Converted directory not found: {converted_dir}")
        sys.exit(1)
    
    # Create preview directory if it doesn't exist
    preview_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all HEIC files
    heic_files = sorted(converted_dir.glob("Src_HDR_P3D65PQ_*_SaveAs_*.heic"))
    
    if not heic_files:
        print(f"⚠ No HEIC files found in {converted_dir}")
        sys.exit(0)
    
    print(f"\n{'='*70}")
    print(f"PNG Preview Generator")
    print(f"{'='*70}\n")
    print(f"Source: {converted_dir}")
    print(f"Output: {preview_dir}")
    print(f"Found {len(heic_files)} HEIC file(s) to convert\n")
    
    # Convert each file
    successful = 0
    failed = 0
    skipped = 0
    
    for idx, heic_file in enumerate(heic_files, 1):
        # Generate PNG filename
        png_file = preview_dir / f"{heic_file.stem}.png"
        
        # Check if PNG already exists and is newer than HEIC
        if png_file.exists():
            heic_mtime = heic_file.stat().st_mtime
            png_mtime = png_file.stat().st_mtime
            
            if png_mtime > heic_mtime:
                print(f"[{idx}/{len(heic_files)}] ⊘ Skipping {heic_file.name} (PNG is up-to-date)")
                skipped += 1
                continue
        
        # Convert file
        print(f"[{idx}/{len(heic_files)}] Converting {heic_file.name}...", end=" ")
        
        if convert_heic_to_png(str(heic_file), str(png_file)):
            print("✓")
            successful += 1
        else:
            print("✗")
            failed += 1
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"Conversion complete!")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Skipped: {skipped}")
    print(f"{'='*70}\n")
    
    # Exit with error code if any conversions failed
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
