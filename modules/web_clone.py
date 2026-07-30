import os
import re
import urllib.parse
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

PRACTICE_PHONE = "27673890946"  # WhatsApp API format
WHATSAPP_LINK = f"https://wa.me/{PRACTICE_PHONE}?text=Hello%20Thembelihle,%20I%20would%20like%20to%20book%20a%20therapy%20session."

visited_urls = set()

def sanitize_folder_name(url):
    parsed = urllib.parse.urlparse(url)
    folder = parsed.netloc + parsed.path
    folder = re.sub(r'[\\/:*?"<>|]', '_', folder).strip('_')
    return folder or "cloned_site"

def get_relative_prefix(depth):
    return "../" * depth if depth > 0 else "./"

def download_asset(asset_url, base_dir):
    try:
        parsed_asset = urllib.parse.urlparse(asset_url)
        asset_path = parsed_asset.path.lstrip('/')
        if not asset_path:
            return asset_url

        local_file_path = os.path.join(base_dir, asset_path)
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

        if not os.path.exists(local_file_path):
            resp = requests.get(asset_url, headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                with open(local_file_path, 'wb') as f:
                    f.write(resp.content)

        return asset_path
    except Exception as e:
        print(f"   [!] Asset Download Error ({asset_url}): {e}")
        return asset_url

def patch_and_enrich_html(soup, rel_prefix):
    """Fixes broken service grids, missing header elements, and dummy booking links."""

    # 1. Fix Booking & Consultation Links
    for a in soup.find_all('a'):
        href = a.get('href', '')
        text = a.get_text().strip().lower()
        if 'book' in text or 'consult' in text or 'url?id=' in href:
            a['href'] = WHATSAPP_LINK
            a['target'] = "_blank"

    # 2. Fix Broken Resource / Blog Articles Links
    for a in soup.find_all('a', href=True):
        if 'resources' in a['href'] or 'pages/resources' in a['href']:
            a['href'] = rel_prefix + "resources.html"

    # 3. Ensure Services Anchor Link standardisation
    for a in soup.find_all('a', href=True):
        if 'services' in a['href'].lower() and not a['href'].startswith('http'):
            a['href'] = rel_prefix + "index.html#services"

    # 4. Inject Contact & POPIA / HPCSA Compliance Footer if missing
    if not soup.find('footer'):
        footer_html = f"""
        <footer style="background-color: #333; color: #fff; padding: 40px 20px; font-family: sans-serif; margin-top: 50px;">
            <div style="max-width: 1100px; margin: 0 auto; display: flex; flex-wrap: wrap; justify-content: space-between; gap: 20px;">
                <div>
                    <h3>Hopeful Seasons Wellness</h3>
                    <p>Clinical Psychology Practice</p>
                    <p>Practitioner: Thembelihle Hope Magubane (Clinical Psychologist)</p>
                </div>
                <div>
                    <h4>Practice Registrations</h4>
                    <p>HPCSA Registered | BHF Registered</p>
                    <p>Direct Medical Aid Claims Available</p>
                </div>
                <div>
                    <h4>Contact & Bookings</h4>
                    <p>Phone / WhatsApp: +27 67 389 0946</p>
                    <p>Location: Johannesburg, South Africa</p>
                    <p><a href="{WHATSAPP_LINK}" target="_blank" style="color: #8fae8b; font-weight: bold;">Book via WhatsApp</a></p>
                </div>
            </div>
            <div style="text-align: center; border-top: 1px solid #555; padding-top: 20px; margin-top: 20px; font-size: 12px; color: #aaa;">
                <p>&copy; Hopeful Seasons Wellness. All rights reserved. POPIA Compliant Medical Practice Disclosure.</p>
            </div>
        </footer>
        """
        soup.body.append(BeautifulSoup(footer_html, 'html.parser'))

    return soup

def clone_page(url, root_domain, base_dir, current_depth, max_depth):
    normalized_url = url.split('#')[0].rstrip('/')
    if normalized_url in visited_urls or current_depth > max_depth:
        return
    visited_urls.add(normalized_url)

    print(f"[+] Crawling (Level {current_depth}): {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"   [!] HTTP {response.status_code} Error: {url}")
            return
    except Exception as e:
        print(f"   [!] Request Failed: {url} -> {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    parsed_page = urllib.parse.urlparse(url)
    path = parsed_page.path.strip('/')
    
    if not path:
        file_name = "index.html"
        folder_depth = 0
    elif path.endswith(".html"):
        file_name = path
        folder_depth = path.count('/')
    else:
        file_name = f"{path}.html"
        folder_depth = file_name.count('/') - 1 if '/' in file_name else 0

    rel_prefix = get_relative_prefix(folder_depth)

    # 1. Localize Images
    for img in soup.find_all('img'):
        src = img.get('src')
        if src:
            full_asset_url = urllib.parse.urljoin(url, src)
            saved_asset_path = download_asset(full_asset_url, base_dir)
            img['src'] = rel_prefix + saved_asset_path

    # 2. Localize Stylesheets
    for link in soup.find_all('link', rel=lambda x: x and 'stylesheet' in x.lower()):
        href = link.get('href')
        if href:
            full_asset_url = urllib.parse.urljoin(url, href)
            saved_asset_path = download_asset(full_asset_url, base_dir)
            link['href'] = rel_prefix + saved_asset_path

    # 3. Localize Scripts
    for script in soup.find_all('script', src=True):
        src = script.get('src')
        if src:
            full_asset_url = urllib.parse.urljoin(url, src)
            saved_asset_path = download_asset(full_asset_url, base_dir)
            script['src'] = rel_prefix + saved_asset_path

    # 4. Patch Navigation, Links, and Missing UI Components
    soup = patch_and_enrich_html(soup, rel_prefix)

    # 5. Recursive Crawl for Subpages
    for a_tag in soup.find_all('a', href=True):
        link_href = a_tag.get('href')
        
        if not link_href or link_href.startswith(('mailto:', 'tel:', 'javascript:', 'https://wa.me')):
            continue

        full_link = urllib.parse.urljoin(url, link_href)
        parsed_link = urllib.parse.urlparse(full_link)

        if parsed_link.netloc == root_domain and current_depth < max_depth:
            clone_page(full_link, root_domain, base_dir, current_depth + 1, max_depth)

    # 6. Save Processed Local File
    file_path = os.path.join(base_dir, file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(soup.prettify())

    print(f"   [✓] Successfully processed and saved -> {file_path}")

def start_cloning():
    print("=" * 60)
    print("      CoAgent Enterprise Deep Cloner & Enriched Builder v3.0")
    print("=" * 60)
    
    target_url = input("\nEnter target website URL: ").strip()
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url

    depth_input = input("Enter crawl depth (Default 3 = Full site + sub-pages): ").strip()
    max_depth = int(depth_input) if depth_input.isdigit() else 3

    parsed_url = urllib.parse.urlparse(target_url)
    root_domain = parsed_url.netloc
    output_folder = sanitize_folder_name(target_url)
    base_dir = os.path.join("cloned_sites", output_folder)

    os.makedirs(base_dir, exist_ok=True)
    visited_urls.clear()

    print(f"\n[+] Starting deep clone for domain: {root_domain}")
    print(f"[+] Output Directory: {os.path.abspath(base_dir)}\n")

    clone_page(target_url, root_domain, base_dir, current_depth=1, max_depth=max_depth)

    print("\n" + "=" * 60)
    print(f"[+] Deep Clone Completed! Root Output: {os.path.abspath(os.path.join(base_dir, 'index.html'))}")
    print("=" * 60)

if __name__ == "__main__":
    start_cloning()