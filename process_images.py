import os
import json
import glob
from PIL import Image, ImageOps
import pyexiv2

SOURCE_DIR = "All"
TARGET_DIR = "review/images"
MANIFEST_FILE = "review/manifest.json"
MAX_SIZE = 1600
JPEG_QUALITY = 80

def process_images():
    if os.path.exists(TARGET_DIR):
        import shutil
        print(f"Cleaning target directory: {TARGET_DIR}")
        shutil.rmtree(TARGET_DIR)
    os.makedirs(TARGET_DIR)

    manifest = {}

    # Gather images (case insensitive)
    image_paths = []
    for ext in ('*.jpg', '*.jpeg', '*.png', '*.tif', '*.tiff'):
        image_paths.extend(glob.glob(os.path.join(SOURCE_DIR, ext), recursive=False))
        image_paths.extend(glob.glob(os.path.join(SOURCE_DIR, ext.upper()), recursive=False))

    # Remove duplicates
    image_paths = list(set(image_paths))
    
    print(f"Found {len(image_paths)} images in {SOURCE_DIR}/")

    for img_path in image_paths:
        filename = os.path.basename(img_path)
        print(f"Processing {filename}...")

        # 1. Read Keywords
        keywords = []
        try:
            with pyexiv2.Image(img_path) as img:
                # Try IPTC
                try:
                    iptc_data = img.read_iptc()
                    if 'Iptc.Application2.Keywords' in iptc_data:
                        kw = iptc_data['Iptc.Application2.Keywords']
                        if isinstance(kw, list):
                            keywords.extend(kw)
                        else:
                            keywords.append(kw)
                except Exception:
                    pass

                # Try XMP (dc:subject is common for keywords in Lightroom/Bridge)
                try:
                    xmp_data = img.read_xmp()
                    if 'Xmp.dc.subject' in xmp_data:
                        subj = xmp_data['Xmp.dc.subject']
                        if isinstance(subj, list):
                            keywords.extend(subj)
                        else:
                            keywords.append(subj)
                except Exception:
                    pass
                
        except Exception as e:
            print(f"  Warning: Could not read metadata for {filename}: {e}")

        # Deduplicate keywords
        keywords = list(set(keywords))
        
        if not keywords:
            print(f"  No keywords found for {filename}. Skipping.")
            continue

        # 2. Resize and Compress Image
        target_path = os.path.join(TARGET_DIR, filename)
        
        # Convert to jpeg if necessary
        base, ext = os.path.splitext(filename)
        if ext.lower() not in ['.jpg', '.jpeg']:
            filename = base + ".jpg"
            target_path = os.path.join(TARGET_DIR, filename)

        try:
            with Image.open(img_path) as pil_img:
                # Exif orientation correction before resizing
                try:
                    pil_img = ImageOps.exif_transpose(pil_img)
                except Exception:
                    pass

                # Convert to RGB if necessary (e.g. RGBA for PNG)
                if pil_img.mode != 'RGB':
                    pil_img = pil_img.convert('RGB')
                
                pil_img.thumbnail((MAX_SIZE, MAX_SIZE), Image.Resampling.LANCZOS)
                
                pil_img.save(target_path, "JPEG", quality=JPEG_QUALITY, optimize=True)
        except Exception as e:
            print(f"  Error processing image {filename}: {e}")
            continue
            
        # 3. Update manifest
        for keyword in keywords:
            if keyword not in manifest:
                manifest[keyword] = []
            if filename not in manifest[keyword]:
                manifest[keyword].append(filename)

    # Output manifest.json
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Processed {len(image_paths)} images.")
    print(f"Manifest saved to {MANIFEST_FILE}")

if __name__ == "__main__":
    process_images()
