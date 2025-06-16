import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import os

def fetch_image_urls(url):
    print(f"[+] Fetching image URLs from {url}...")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[!] Failed to fetch page: {e}")
        return []
    soup = BeautifulSoup(response.content, 'html.parser')
    img_tags = soup.find_all('img')
    img_urls = []
    
    for img in img_tags:
        if 'src' in img.attrs:
            src = img['src']
            # Handle relative URLs
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                from urllib.parse import urljoin
                src = urljoin(url, src)
            elif not src.startswith('http'):
                from urllib.parse import urljoin
                src = urljoin(url, src)
            img_urls.append(src)
    
    return img_urls

def download_images(img_urls, images_folder="images"):
    images = []
    print(f"[+] Downloading {len(img_urls)} images...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Create images folder if it doesn't exist
    try:
        os.makedirs(images_folder, exist_ok=True)
    except Exception as e:
        print(f"[!] Failed to create images folder: {e}")
        return images
    
    for idx, url in enumerate(img_urls):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Skip very small images (likely ads or icons)
            if len(response.content) < 1000:
                continue
                
            img = Image.open(BytesIO(response.content)).convert("RGB")
            
            # Skip very small images by dimensions
            if img.width < 100 or img.height < 100:
                continue
            
            # Save image to images folder
            img_filename = os.path.join(images_folder, f"image_{idx+1:03d}.jpg")
            try:
                img.save(img_filename, "JPEG", quality=90)
            except Exception as e:
                print(f"  ! Failed to save image {img_filename}: {e}")
                continue
            
            images.append(img)
            print(f"  - Downloaded and saved image {idx+1}/{len(img_urls)} ({img.width}x{img.height})")
        except requests.RequestException as e:
            print(f"  ! Failed to download {url}: {e}")
        except Exception as e:
            print(f"  ! Error processing image from {url}: {e}")
    
    return images

def create_pdf_pages(images, max_height=60000):
    """Split images into pages that don't exceed PIL's limits"""
    print("[+] Creating PDF pages...")
    pages = []
    current_page_images = []
    current_height = 0
    max_width = max((img.width for img in images), default=800)
    
    for img in images:
        # If adding this image would exceed the limit, create a new page
        if current_height + img.height > max_height and current_page_images:
            # Create page from current images
            page_img = Image.new('RGB', (max_width, current_height), (255, 255, 255))
            y_offset = 0
            for page_img_item in current_page_images:
                page_img.paste(page_img_item, (0, y_offset))
                y_offset += page_img_item.height
            pages.append(page_img)
            
            # Start new page
            current_page_images = [img]
            current_height = img.height
        else:
            current_page_images.append(img)
            current_height += img.height
    
    # Add the last page if there are remaining images
    if current_page_images:
        page_img = Image.new('RGB', (max_width, current_height), (255, 255, 255))
        y_offset = 0
        for img in current_page_images:
            page_img.paste(img, (0, y_offset))
            y_offset += img.height
        pages.append(page_img)
    
    print(f"  - Created {len(pages)} pages")
    return pages

def save_as_pdf(pages, output_file):
    """Save multiple pages as a single PDF"""
    print(f"[+] Saving PDF as {output_file}")
    
    if not pages:
        print("[!] No pages to save")
        return
    
    try:
        # Save first page and append the rest
        if len(pages) == 1:
            pages[0].save(output_file, "PDF", resolution=100.0, quality=85)
        else:
            pages[0].save(
                output_file, 
                "PDF", 
                resolution=100.0, 
                quality=85,
                save_all=True, 
                append_images=pages[1:]
            )
        print(f"[✓] PDF saved successfully with {len(pages)} pages")
    except Exception as e:
        print(f"[!] Error saving PDF: {e}")
        # Fallback: save as individual images
        print("[+] Saving as individual images instead...")
        base_name = output_file.replace('.pdf', '')
        for i, page in enumerate(pages):
            try:
                page.save(f"{base_name}_page_{i+1}.png", "PNG")
            except Exception as img_e:
                print(f"[!] Failed to save fallback image {i+1}: {img_e}")
        print(f"[✓] Saved {len(pages)} individual PNG files")

def main():
    chapter_url = "https://www.sololevelingmangafree.com/manga/solo-leveling-chapter-148/index.html"
    output_pdf = "Solo_Leveling_Chapter_148.pdf"
    images_folder = "images"
    
    try:
        img_urls = fetch_image_urls(chapter_url)
        print(f"[+] Found {len(img_urls)} image URLs")
        
        if not img_urls:
            print("[!] No image URLs found. The website structure might have changed.")
            return
        
        images = download_images(img_urls, images_folder=images_folder)
        
        if not images:
            print("[!] No images were downloaded. Aborting.")
            return
        
        print(f"[+] Successfully downloaded and saved {len(images)} images")
        
        pages = create_pdf_pages(images)
        save_as_pdf(pages, output_pdf)
        
        print("[✓] Done!")
        
    except Exception as e:
        print(f"[!] An error occurred: {e}")

if __name__ == "__main__":
    main()