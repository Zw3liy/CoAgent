import os
import re
import sys
import urllib.parse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print('[!] Dependencies missing. Please run: pip install requests beautifulsoup4')
    sys.exit(1)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def format_url(url):
    if not url.startswith(('http://', 'https://')):
        return 'https://' + url
    return url

def run_seo_audit(url):
    url = format_url(url)
    print(f'\n[=== ADVANCED SEO AUDIT: {url} ===]')
    try:
        res = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.title.string.strip() if soup.title and soup.title.string else 'MISSING'
        meta_desc = 'MISSING'
        desc_tag = soup.find('meta', attrs={'name': re.compile(r'description', re.I)})
        if desc_tag and desc_tag.get('content'):
            meta_desc = desc_tag['content'].strip()
        h1_tags = [h1.get_text(strip=True) for h1 in soup.find_all('h1')]
        imgs = soup.find_all('img')
        missing_alt = [img for img in imgs if not img.get('alt')]
        links = soup.find_all('a', href=True)
        print(f'[+] Status Code: {res.status_code}')
        print(f'[+] Page Title ({len(title)} chars): {title}')
        print(f'[+] Meta Description ({len(meta_desc)} chars): {meta_desc}')
        print(f'[+] H1 Headings Found ({len(h1_tags)}): {h1_tags[:3]}')
        print(f'[+] Images Analyzed: {len(imgs)} | Missing ALT tags: {len(missing_alt)}')
        print(f'[+] Internal/External Links Found: {len(links)}')
    except Exception as e:
        print(f'[-] SEO Audit failed: {e}')

def run_site_clone(url):
    url = format_url(url)
    print(f'\n[=== ADVANCED WEBSITE CLONER: {url} ===]')
    dom = urllib.parse.urlparse(url).netloc.replace(':', '_')
    out = os.path.join('cloned_sites', dom)
    imgs_dir = os.path.join(out, 'images')
    os.makedirs(imgs_dir, exist_ok=True)
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        img_tags = soup.find_all('img')
        print(f'[*] Extracting and saving {len(img_tags)} image assets...')
        for i, img in enumerate(img_tags, 1):
            src = img.get('src') or img.get('data-src')
            if not src:
                continue
            full_src = urllib.parse.urljoin(url, src)
            iname = os.path.basename(urllib.parse.urlparse(full_src).path) or f'asset_{i}.jpg'
            try:
                img_bytes = requests.get(full_src, headers=HEADERS, timeout=8).content
                with open(os.path.join(imgs_dir, iname), 'wb') as f:
                    f.write(img_bytes)
                img['src'] = os.path.join('images', iname)
            except Exception:
                pass
        with open(os.path.join(out, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print(f'[+] Cloned successfully into: {os.path.abspath(out)}')
    except Exception as e:
        print(f'[-] Site Clone failed: {e}')

def run_web_search(query):
    print(f'\n[=== AGENT WEB SEARCH DIAGNOSTIC: {query} ===]')
    search_url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}'
    try:
        res = requests.get(search_url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(res.text, 'html.parser')
        results = soup.find_all('a', class_='result__url')
        snippets = soup.find_all('a', class_='result__snippet')
        print(f'[+] Top Search Results for query standard:')
        for i, (r, s) in enumerate(zip(results[:5], snippets[:5]), 1):
            print(f'  {i}. {r.get_text(strip=True)}')
            print(f'     Snippet: {s.get_text(strip=True)}\n')
    except Exception as e:
        print(f'[-] Search Diagnostic failed: {e}')

def main():
    while True:
        print('\n===================================================')
        print('         CoAgent Web & SEO Intelligence Engine      ')
        print('===================================================')
        print('1. Website Cloner (HTML + Full Asset Extraction)')
        print('2. Automated SEO Audit & Diagnostic')
        print('3. Full Execution (Clone Site + Run SEO Audit)')
        print('4. Automated Query Search Diagnostic')
        print('5. Return to Master Task Menu')
        print('===================================================')
        choice = input('Select an action (1-5): ').strip()

        if choice == '1':
            u = input('Enter URL to clone: ').strip()
            if u: run_site_clone(u)
        elif choice == '2':
            u = input('Enter URL for SEO audit: ').strip()
            if u: run_seo_audit(u)
        elif choice == '3':
            u = input('Enter target URL: ').strip()
            if u:
                run_site_clone(u)
                run_seo_audit(u)
        elif choice == '4':
            q = input('Enter search query: ').strip()
            if q: run_web_search(q)
        elif choice == '5':
            break
        else:
            print('[-] Invalid selection.')

if __name__ == '__main__':
    main()