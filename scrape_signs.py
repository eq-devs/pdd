#!/usr/bin/env python3
"""Scraper for Kazakhstan traffic signs from safety-driving.kz"""

import re
import json
import urllib.request
from html.parser import HTMLParser

URL = "https://safety-driving.kz/kz/pdd/"

class SignParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.signs = []
        self.images = []
        self.in_sign_section = False
        self.current_tag = None
        self.current_attrs = {}
        self.text_buffer = ""
        self.all_imgs = []
        self.all_text_near_imgs = []
        self.collecting_text = False
        self.depth = 0
        self.img_parent_depth = -1
        
    def handle_starttag(self, tag, attrs):
        self.depth += 1
        attrs_dict = dict(attrs)
        self.current_tag = tag
        self.current_attrs = attrs_dict
        
        if tag == 'img':
            src = attrs_dict.get('src', '') or attrs_dict.get('data-src', '') or attrs_dict.get('data-lazy-src', '')
            alt = attrs_dict.get('alt', '')
            title = attrs_dict.get('title', '')
            if src:
                self.all_imgs.append({
                    'src': src,
                    'alt': alt,
                    'title': title,
                })

    def handle_endtag(self, tag):
        self.depth -= 1

    def handle_data(self, data):
        pass

def extract_signs_from_html(html_content):
    """Extract traffic signs data from the raw HTML."""
    
    # Find all img tags and their surrounding context
    img_pattern = re.compile(
        r'<img[^>]*?(?:src|data-src|data-lazy-src)=["\']([^"\']+)["\'][^>]*?>',
        re.IGNORECASE | re.DOTALL
    )
    
    all_images = []
    for match in img_pattern.finditer(html_content):
        src = match.group(1)
        # Get alt attribute  
        alt_match = re.search(r'alt=["\']([^"\']*)["\']', match.group(0))
        alt = alt_match.group(1) if alt_match else ''
        title_match = re.search(r'title=["\']([^"\']*)["\']', match.group(0))
        title = title_match.group(1) if title_match else ''
        
        all_images.append({
            'src': src,
            'alt': alt,
            'title': title,
            'pos': match.start()
        })
    
    return all_images

def main():
    print("Fetching page...")
    req = urllib.request.Request(URL, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    with urllib.request.urlopen(req, timeout=30) as response:
        html = response.read().decode('utf-8')
    
    print(f"Page size: {len(html)} bytes")
    
    # Save raw HTML for analysis
    with open('/Users/estai/Desktop/pdd/raw_page.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("HTML saved to raw_page.html")
    
    # Extract all images
    images = extract_signs_from_html(html)
    print(f"\nTotal images found: {len(images)}")
    
    # Filter for traffic sign images
    sign_images = []
    for img in images:
        src = img['src']
        # Traffic sign images typically have specific patterns
        if any(keyword in src.lower() for keyword in ['znak', 'sign', 'pdd', 'belg', 'upload', 'media']):
            sign_images.append(img)
        elif '/upload/' in src:
            sign_images.append(img)
    
    print(f"Potential sign images: {len(sign_images)}")
    
    # Print all images for analysis
    print("\n=== ALL IMAGES ===")
    for i, img in enumerate(images):
        print(f"{i}: src={img['src'][:100]}, alt={img['alt'][:50]}")
    
    # Save results
    with open('/Users/estai/Desktop/pdd/all_images.json', 'w', encoding='utf-8') as f:
        json.dump(images, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved {len(images)} images to all_images.json")

if __name__ == '__main__':
    main()
