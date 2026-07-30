import os, urllib.parse, sys
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print('[!] Run: pip install requests beautifulsoup4')
    sys.exit(1)

def clone(url):
    if not url.startswith(('http://','https://')): url = 'https://' + url
    dom = urllib.parse.urlparse(url).netloc.replace(':', '_')
    out = os.path.join('cloned_sites', dom)
    imgs = os.path.join(out, 'images')
    os.makedirs(imgs, exist_ok=True)
    headers = {'User-Agent': 'Mozilla/5.0'}
    print(f'[*] Cloning {url}...')
    res = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(res.text, 'html.parser')
    for i, img in enumerate(soup.find_all('img'), 1):
        src = img.get('src') or img.get('data-src')
        if not src: continue
        full = urllib.parse.urljoin(url, src)
        iname = os.path.basename(urllib.parse.urlparse(full).path) or f'img_{i}.jpg'
        try:
            data = requests.get(full, headers=headers, timeout=10).content
            with open(os.path.join(imgs, iname), 'wb') as f: f.write(data)
            img['src'] = os.path.join('images', iname)
        except Exception as e: pass
    with open(os.path.join(out, 'index.html'), 'w', encoding='utf-8') as f: f.write(soup.prettify())
    print(f'[+] Site cloned to {os.path.abspath(out)}')

if __name__ == '__main__':
    u = input('Enter URL to clone: ').strip()
    if u: clone(u)
