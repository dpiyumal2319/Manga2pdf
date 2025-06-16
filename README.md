# Manga to PDF Converter

A Python script that downloads manga chapters from websites and converts them into PDF format for offline reading.

## Features

- 🔽 Downloads all images from a manga chapter URL
- 📄 Creates multi-page PDFs (handles PIL's image size limitations)
- 🖼️ Filters out ads and small unwanted images
- 🔄 Fallback to PNG images if PDF creation fails
- 📱 Handles various image URL formats and relative paths
- ⚡ Progress tracking with detailed logging

## Requirements

- Python 3.6+
- Internet connection for downloading images

## Installation

1. Clone or download this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

1. Edit the `main()` function in `main.py` to set your desired manga chapter URL:
```python
chapter_url = "https://example-manga-site.com/chapter-1/"
output_pdf = "Chapter_1.pdf"
```

2. Run the script:
```bash
python main.py
```

### Customization

You can modify the following parameters in the code:

- `max_height` in `create_pdf_pages()`: Maximum height per PDF page (default: 60,000 pixels)
- `quality` in `save_as_pdf()`: JPEG compression quality (default: 85)
- Image filtering thresholds in `download_images()`

## How It Works

1. **Fetches HTML**: Downloads the webpage and parses it for image URLs
2. **Downloads Images**: Downloads all manga page images with proper headers
3. **Filters Content**: Removes small images (ads, icons) based on size and dimensions
4. **Creates Pages**: Groups images into pages that don't exceed PIL's limits
5. **Generates PDF**: Creates a multi-page PDF or falls back to individual PNG files

## Supported Sites

This script works with websites that serve manga images directly in `<img>` tags. It may need modifications for sites that:
- Use JavaScript to load images dynamically
- Require authentication
- Use non-standard image serving methods

## File Structure

```
manga-to-pdf/
├── main.py              # Main script
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── output/             # Generated PDFs (created automatically)
```

## Troubleshooting

### Common Issues

**No images downloaded:**
- Check if the website URL is correct
- The site might have changed its structure
- Try adding delay between requests if being rate-limited

**PDF creation fails:**
- The script will automatically fall back to PNG images
- Check available disk space
- Verify image dimensions aren't corrupted

**Download errors:**
- Some sites block automated requests
- Try modifying the User-Agent string
- Check your internet connection

### Error Messages

- `"Maximum supported image dimension is 65500 pixels"`: The script handles this automatically by splitting into multiple pages
- `"broken data stream"`: Fixed by the multi-page approach
- `"No image URLs found"`: The website structure might have changed

## Legal Notice

This tool is for educational purposes only. Please respect copyright laws and website terms of service. Only download content you have the right to access, and consider supporting manga creators by purchasing official releases.

## Contributing

Feel free to submit issues and enhancement requests! Some areas for improvement:
- Support for JavaScript-heavy sites
- GUI interface
- Batch processing multiple chapters
- Custom image processing options

## License

This project is open source. Use responsibly and at your own risk.