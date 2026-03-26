import os
import re
import json

def get_images(base_dir):
    data = {}
    for root, _, files in os.walk(base_dir):
        # determine category
        rel = os.path.relpath(root, base_dir)
        if rel == ".":
            cat = "Screenshots"
        else:
            cat = rel.title()
            if cat == "Rule":
                cat = "Rules"
        
        imgs = []
        for f in files:
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
                imgs.append(os.path.join(root, f))
        
        if imgs:
            # We must store them as relative URLs e.g. "images/file.png"
            urls = []
            for img in imgs:
                url_path = os.path.relpath(img, os.path.dirname(base_dir))
                # replace backslashes on windows just in case
                urls.append(url_path.replace(os.sep, '/'))
            # sort them naturally or alphabetically
            data[cat] = sorted(urls)
            
    return data

def main():
    project_dir = "/Users/estai/Desktop/pdd"
    images_dir = os.path.join(project_dir, "images")
    index_path = os.path.join(project_dir, "index.html")
    
    gallery_data = get_images(images_dir)
    
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Generate the JS object
    js_object = json.dumps(gallery_data, indent=4, ensure_ascii=False)
    
    # We want to replace const galleryData = { ... };
    pattern = re.compile(r"const\s+galleryData\s*=\s*\{.*?\};", re.DOTALL)
    
    if not pattern.search(content):
        print("Error: Could not find 'const galleryData = {...};' in index.html")
        return
        
    new_content = pattern.sub(f"const galleryData = {js_object};", content)
    
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(new_content)
        
    print(f"✅ index.html updated successfully with {sum(len(v) for v in gallery_data.values())} images!")

if __name__ == "__main__":
    main()
