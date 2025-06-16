import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import os
from urllib.parse import urljoin

def fetch_image_urls(url):
    """
    Fetches all image URLs from a given webpage URL.
    Handles relative and absolute paths.
    """
    print(f"[+] Fetching image URLs from {url}...")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[!] Error fetching URL: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    img_tags = soup.find_all('img')
    img_urls = []

    for img in img_tags:
        if 'src' in img.attrs:
            src = img['src'].strip()
            # Construct absolute URL from relative path
            if not src.startswith(('http://', 'https://')):
                src = urljoin(url, src)
            img_urls.append(src)
            
    print(f"[+] Found {len(img_urls)} potential image URLs.")
    return img_urls

def download_images(img_urls):
    """
    Downloads images from a list of URLs and returns them as PIL Image objects.
    Filters out small or invalid images.
    """
    images = []
    print(f"[+] Downloading {len(img_urls)} images...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.google.com/' # Adding a referer can sometimes help
    }
    
    for idx, url in enumerate(img_urls):
        try:
            # Get the image content
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Skip very small images (likely ads, spacers, or icons) based on content size
            if len(response.content) < 2000: # Increased threshold slightly
                print(f"  - Skipping image {idx+1}/{len(img_urls)} (file size too small)")
                continue
            
            # Open the image with Pillow
            img = Image.open(BytesIO(response.content)).convert("RGB")
            
            # Skip very small images based on dimensions
            if img.width < 100 or img.height < 100:
                print(f"  - Skipping image {idx+1}/{len(img_urls)} (dimensions too small: {img.width}x{img.height})")
                continue
            
            images.append(img)
            print(f"  - Downloaded image {idx+1}/{len(img_urls)} ({img.width}x{img.height})")
            
        except requests.RequestException as e:
            print(f"  ! Failed to download {url}: {e}")
        except Image.DecompressionBombError:
            print(f"  ! DecompressionBombError for {url}. Image is too large to process.")
        except Exception as e:
            print(f"  ! An unexpected error occurred for {url}: {e}")
    
    return images

def save_as_pdf(pages, output_file):
    """
    Saves a list of PIL Image objects as a single, multi-page PDF.
    Each image in the list becomes a separate page.
    """
    print(f"[+] Saving PDF as {output_file}...")
    
    if not pages:
        print("[!] No pages to save. Aborting PDF creation.")
        return
    
    try:
        # The first image is saved, and the rest are appended
        pages[0].save(
            output_file, 
            "PDF", 
            resolution=100.0, 
            save_all=True, 
            append_images=pages[1:] # Pass the rest of the images to be appended
        )
        print(f"[✓] PDF saved successfully with {len(pages)} pages.")
    except Exception as e:
        print(f"[!] Error saving PDF: {e}")

def main():
    """
    Main function to run the manga downloader.
    """
    # URL of the manga chapter you want to download
    chapter_url = "https://www.sololevelingmangafree.com/manga/solo-leveling-chapter-148/index.html"
    
    # Name of the output PDF file
    output_pdf = "Solo_Leveling_Chapter_148.pdf"
    
    try:
        # Step 1: Get all image URLs from the chapter page
        img_urls = fetch_image_urls(chapter_url)
        
        if not img_urls:
            print("[!] No image URLs found. The website structure might have changed or the URL is incorrect.")
            return
        
        # Step 2: Download the images
        images = download_images(img_urls)
        
        if not images:
            print("[!] No valid images were downloaded. Aborting PDF creation.")
            return
            
        print(f"[+] Successfully downloaded {len(images)} valid images.")
        
        # Step 3: Save the downloaded images directly into a PDF
        # Each image will be its own page, fixing the original issue.
        save_as_pdf(images, output_pdf)
        
        print("\n[✓] Done!")
        
    except Exception as e:
        print(f"\n[!] An unexpected error occurred in the main process: {e}")

if __name__ == "__main__":
    main()
