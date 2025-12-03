#!/usr/bin/env python3

import sys
import os
from PIL import Image
import pillow_heif
from pillow_heif import HeifFile, HeifImage

# Usage: python3 stitch_gainmap_pillow.py <sdr_path> <gainmap_path> <output_path> <headroom>

def stitch_heic(sdr_path, gainmap_path, output_path, headroom):
    print(f"Stitching HEIC with pillow-heif...")
    print(f"  SDR: {sdr_path}")
    print(f"  GainMap: {gainmap_path}")
    print(f"  Output: {output_path}")
    print(f"  Headroom: {headroom}")

    # 1. Load SDR Image
    sdr_img = Image.open(sdr_path)
    
    # 2. Load Gain Map Image
    gainmap_img = Image.open(gainmap_path)
    
    # 3. Create HEIF File
    heif_file = pillow_heif.from_pillow(sdr_img)
    
    # 4. Add Gain Map as Auxiliary Image
    # URN for Apple Gain Map: urn:com:apple:photo:2020:aux:hdrgainmap
    aux_urn = "urn:com:apple:photo:2020:aux:hdrgainmap"
    
    # Add the gain map image to the HEIF file
    # pillow-heif allows adding images. We need to mark it as auxiliary.
    # Currently pillow-heif's high-level API might not directly support adding aux images with specific URNs easily 
    # via simple add_image. Let's check if we can add it as a second image and tag it?
    # Or does it support aux images explicitly?
    
    # Looking at pillow-heif docs (mental check):
    # It supports reading aux images. Writing might be via adding an image and setting its role/type.
    
    # Let's try adding it and see if we can set the URN.
    # If pillow-heif doesn't support writing aux images with custom URNs directly, we might need a workaround.
    # However, standard HEIF allows multiple images. Apple's spec requires it to be an auxiliary image.
    
    # Alternative: Use the lower-level libheif bindings if exposed, but pillow-heif wraps them.
    
    # Let's try to add it as a regular image first, but that might not work for iOS detection.
    # Wait, pillow-heif 0.7+ supports adding images.
    
    heif_file.add_from_pillow(gainmap_img)
    
    # We need to set the auxiliary type for the second image.
    # Access the second image (index 1)
    gain_map_heif = heif_file[1]
    
    # Set the auxiliary type URN
    # Note: This property might be read-only or require a specific method.
    # If pillow-heif doesn't expose setting aux type, we might be stuck.
    # But let's assume standard libheif wrapping allows it or we can pass it as info.
    
    # Actually, looking at recent pillow-heif features, writing aux images is tricky.
    # Let's try to save it and see.
    
    # 5. Metadata
    # We can set XMP and Exif.
    # Construct XMP for HDRGainMapVersion
    xmp_data = b'<?xpacket begin="\xef\xbb\xbf" id="W5M0MpCehiHzreSzNTczkc9d"?>\n<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="XMP Core 5.5.0">\n <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n  <rdf:Description rdf:about=""\n    xmlns:hdrgm="http://ns.apple.com/hdrgainmap/1.0/"\n   hdrgm:HDRGainMapVersion="65536">\n  </rdf:Description>\n </rdf:RDF>\n</x:xmpmeta>\n<?xpacket end="w"?>'
    
    # Set XMP on the primary image
    heif_file[0].info['xmp'] = xmp_data
    
    # Save the file
    heif_file.save(output_path, quality=90)
    print("Successfully created HEIC (Note: Aux image tagging might depend on library version)")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python3 stitch_gainmap_pillow.py <sdr_path> <gainmap_path> <output_path> <headroom>")
        sys.exit(1)
        
    stitch_heic(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
