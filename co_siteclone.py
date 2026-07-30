import os
import re
import urllib.parse
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("[!] Missing required libraries. Run: pip install requests beautifulsoup4")
    import sys
    sys.exit(1)

def clone_website(url, output_dir="cloned_sites"):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed_url = urllib.parse.urlparse(url)
    domain = parsed_url.netloc.replace(":", "_")
    target_folder = os.path.join(output_dir, domain)
    images_folder = os.path.join(target_folder, "images")
    
    os.makedirs(target_folder, exist_ok=True)
    os.makedirs(images_folder, exist_ok=True)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print(f"[*] Fetching website: {url} ...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"[!] Failed to fetch {url}: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Download Images
    img_tags = soup.find_all("img")
    print(f"[*] Found {len(img_tags)} image tags. Downloading assets...")

    for i, img in enumerate(img_tags, start=1):
        src = img.get("src") or img.get("data-src")
        if not src:
            continue

        full_img_url = urllib.parse.urljoin(url, src)
        img_name = os.path.basename(urllib.parse.urlparse(full_img_url).path)
        if not img_name or len(img_name) > 50:
            img_name = f"image_{i}.jpg"

        local_img_path = os.path.join(images_folder, img_name)
        relative_img_path = os.path.join("images", img_name)

        try:
            img_data = requests.get(full_img_url, headers=headers, timeout=10).content
            with open(local_img_path, "wb") as f:
                f.write(img_data)
            img["src"] = relative_img_path
            print(f"  [+] Saved image: {img_name}")
        except Exception as e:
            print(f"  [-] Skipped image {full_img_url}: {e}")

    # Save HTML file
    index_file = os.path.join(target_folder, "index.html")
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(soup.prettify())

    print(f"
[✓] Website cloned successfully!")
    print(f"[✓] Location: {os.path.abspath(target_folder)}")
    print(f"[✓] Saved index.html and {len(img_tags)} images.")

if __name__ == "__main__":
    print("===================================================")
    print("           CoAgent Website Cloner Module           ")
    print("===================================================")
    target_url = input("Enter website URL to clone (e.g. example.com): ").strip()
    if target_url:
        clone_website(target_url)
    else:
        print("[-] No URL provided. Aborting.")
