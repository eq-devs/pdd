#!/usr/bin/env python3
"""Generate the premium traffic signs website from wiki_signs.json data."""

import os
import json
import html as html_mod
from datetime import datetime

# Section metadata: Design info, emoji, labels
SECTION_META = {
    "Ескерту белгілері": {
        "css": "warning",
        "emoji": "⚠️",
        "num": "01",
        "desc": "Жүргізушілерге жолдың қауіпті учаскесіне жақындағаны туралы хабарлайды",
        "nav": "⚠️ Ескерту",
    },
    "Басымдылық белгілері": {
        "css": "priority",
        "emoji": "🔶",
        "num": "02",
        "desc": "Жол қиылыстарынан өту кезектілігін белгілейді",
        "nav": "🔶 Басымдық",
    },
    "Тыйым салатын белгілер": {
        "css": "prohibit",
        "emoji": "🚫",
        "num": "03",
        "desc": "Жол жүрісіне белгілі бір шектеулер енгізеді немесе оларды жояды",
        "nav": "🚫 Тыйым",
    },
    "Нұсқайтын белгілер": {
        "css": "mandatory",
        "emoji": "🔵",
        "num": "04",
        "desc": "Белгілерде бағыттауыштармен көрсетілген бағыттарда ғана жүруге рұқсат етіледі",
        "nav": "🔵 Нұсқайтын",
    },
    "Ақпараттық-нұсқағыш белгілер": {
        "css": "info",
        "emoji": "ℹ️",
        "num": "05",
        "desc": "Жүрістің белгілі бір режимдерін енгізеді, елді мекендер мен объектілер туралы хабарлайды",
        "nav": "ℹ️ Ақпараттық",
    },
    "Ақпараттық белгілер": {
        "css": "info",
        "emoji": "ℹ️",
        "num": "05",
        "desc": "Жүрістің белгілі бір режимдерін енгізеді, елді мекендер мен объектілер туралы хабарлайды",
        "nav": "ℹ️ Ақпараттық",
    },
    "Сервис белгілері": {
        "css": "service",
        "emoji": "🅿️",
        "num": "06",
        "desc": "Тиісті объектілердің орналасуы туралы хабардар етеді",
        "nav": "🅿️ Сервис",
    },
    "Қосымша ақпарат белгілері (тақтайшалар)": {
        "css": "supplement",
        "emoji": "📋",
        "num": "07",
        "desc": "Олармен қолданылатын белгілерді нақтылайды немесе шектейді",
        "nav": "📋 Қосымша",
    },
    "Жол таңбасы": {
        "css": "marking",
        "emoji": "🛣️",
        "num": "08",
        "desc": "Жол бетіне салынған сызықтар мен жазулар",
        "nav": "🛣️ Таңбалау",
    },
    "Бағдаршам / Таным белгілер": {
        "css": "traffic",
        "emoji": "🚦",
        "num": "09",
        "desc": "Қозғалысты реттейтін сигналдар және арнайы таным белгілері",
        "nav": "🚦 Бағдаршам",
    }
}

MANUAL_SECTIONS = [
    {
        "title": "Жол таңбасы",
        "signs": [
            {"number": "1.1", "name": "Көлденең таңба", "description": "Жүріс бөлігінің бетіне түсірілген сызықтар, бағыттауыштар және басқа да белгілер.", "src": "https://safety-driving.kz/upload/medialibrary/22e/zrcy68r42pnljux3o5dhddo4ulr6022a/road_1.jpg"},
            {"number": "1.2", "name": "Тік таңба", "description": "Жол құрылыстарының элементтеріне network және жол жабдықтарына түсірілетін сызықтар мен таңбалар.", "src": "https://safety-driving.kz/upload/medialibrary/556/1ga83xj41rk3sktqmd40zgbxy1hgsagg/road_2.jpg"},
            {"number": "1.3", "name": "Арнайы таңба", "description": "Жүріс бетіне жазылатын бағыттаушылар мен жазулар.", "src": "https://safety-driving.kz/upload/medialibrary/fd1/ti0roofuvyfhbuo0q5xhpx5upp9ejcvd/road_3.jpg"}
        ]
    },
    {
        "title": "Бағдаршам / Таным белгілер",
        "signs": [
            {"number": "🚦", "name": "Бағдаршамдар (Қазақстан)", "description": "Жол қозғалысын жарық сигналдары арқылы реттейтін құрылғылар.", "src": "https://safety-driving.kz/upload/medialibrary/534/9wty6ere7hbkugeo0hipnufv5vyqm7cu/traffic_lights_kz.jpg"},
            {"number": "🆔", "name": "Таным белгілер", "description": "Автокөліктерге қойылатын арнайы таным жапсырмалары.", "src": "https://safety-driving.kz/upload/medialibrary/8d2/prx6s1clbjeg4yuy33zs5a0igx1z35pq/other_signs_kz.jpg"}
        ]
    }
]

def e(text):
    return html_mod.escape(str(text or ""), quote=True)

def get_images(base_dir):
    data = {}
    if not os.path.exists(base_dir):
        print(f"Warning: {base_dir} not found.")
        return data
        
    for root, _, files in os.walk(base_dir):
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
                if f.startswith('.'): continue
                imgs.append(os.path.join(root, f))
        
        if imgs:
            urls = []
            for img in imgs:
                url_path = os.path.relpath(img, os.path.dirname(base_dir))
                urls.append(url_path.replace(os.sep, '/'))
            data[cat] = sorted(urls)
            
    return data

def generate_html(sections, gallery_data):
    # Ensure manual sections are added
    existing_titles = [s["title"] for s in sections]
    for ms in MANUAL_SECTIONS:
        if ms["title"] not in existing_titles:
            sections.append(ms)

    nav_links = []
    content_html = []
    
    for i, section in enumerate(sections):
        title = section["title"]
        meta = SECTION_META.get(title, {"css":"info", "emoji":"📌", "num":f"{i+1:02d}", "desc":"", "nav":title[:10]})
        sid = f"s{i+1}"
        
        # Nav Link
        active = " active" if i == 0 else ""
        nav_links.append(f'<a href="#{sid}" class="nav-link{active}" data-cat="{sid}">{meta["nav"]}</a>')
        
        # Signs Grid
        signs_html = []
        for sign in section["signs"]:
            num = e(sign.get("number", ""))
            name = e(sign.get("name", ""))
            desc = e(sign.get("description", ""))
            src = sign.get("src", "")
            
            img_html = f'<div class="img-container"><img src="{e(src)}" alt="{name}" loading="lazy" class="sign-icon"></div>' if src else '<div class="img-container empty"></div>'
            
            signs_html.append(f"""
      <div class="sign-card">
        {img_html}
        <div class="sign-info">
          <span class="sign-badge">{num}</span>
          <div class="sign-name">{name}</div>
          <div class="sign-desc">{desc}</div>
        </div>
      </div>""")
            
        # Section
        content_html.append(f"""
    <section class="sign-section" id="{sid}">
      <div class="section-header">
        <div class="section-icon">{meta['emoji']}</div>
        <div class="section-title">
          <h2>{e(title)}</h2>
          <p>{e(meta['desc'])}</p>
        </div>
      </div>
      <div class="signs-grid">
        {"".join(signs_html)}
      </div>
    </section>""")

    nav_html = "".join(nav_links)
    main_html = "".join(content_html)
    update_time = datetime.now().strftime("%d.%m.%Y %H:%M")
    total_signs = sum(len(s["signs"]) for s in sections)
    
    total_gallery = sum(len(v) for v in gallery_data.values())
    gallery_json = json.dumps(gallery_data, indent=2, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="kk">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ҚР Жол белгілері 2026 — Премиум Анықтамалық</title>
  <meta name="description" content="Қазақстан Республикасының барлық жол белгілері мен таңбалары. Премиум дизайн мен толық ақпарат.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Space+Mono:wght@700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css?v={int(datetime.now().timestamp())}">
</head>
<body>

<header class="hero">
  <div class="container">
    <div class="hero-badge">🇰🇿 Қазақстан Республикасы • ІІМ Стандарты</div>
    <h1>Жол белгілері <span class="year">2026</span></h1>
    <p class="hero-sub">Қазақстан жол белгілері мен таңбаларының ең толық жаңартылған интерактивті анықтамалығы</p>
    
    <div class="search-container">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" id="searchInput" placeholder="Белгіні нөмірі немесе аты бойынша іздеу..." autocomplete="off">
      </div>
    </div>
    
    <div class="hero-stats" style="margin-top: 24px; opacity: 0.6; font-size: 14px;">
        {total_signs} элемент • {len(sections)} санат • Соңғы жаңарту: {update_time}
    </div>

    <button class="gallery-trigger" id="openGallery">
      <span class="icon">🖼️</span>
      Галереяны қарау ({total_gallery} сурет)
    </button>
  </div>
</header>

<nav class="nav-bar">
  <div class="container nav-inner">
    {nav_html}
  </div>
</nav>

<main class="container">
  {main_html}
</main>

<footer>
  <div class="container">
    <div class="footer-grid">
      <div class="footer-info">
        <h3>🚗 ҚР Жол Белгілері</h3>
        <p>Деректер көзі: <a href="https://kk.wikipedia.org/wiki/Қазақстан_жол_белгілері" target="_blank">Wikipedia</a></p>
      </div>
      <div>
        <p>© 2026 Анықтамалық. Барлық құқықтар қорғалған.</p>
      </div>
    </div>
  </div>
</footer>

<div class="viewer-overlay" id="viewerOverlay">
  <div class="viewer-close" id="closeViewer">✕</div>
  <div class="viewer-container">
    <img src="" id="viewerImg" alt="Viewer Image">
  </div>
  <div class="viewer-bottom-nav">
    <div class="viewer-nav prev" id="prevBtn">←</div>
    <div class="viewer-info-pill">
      <div id="imageName" style="color:#fff;font-size:13px;opacity:0.8;max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"></div>
      <div class="viewer-counter"><span id="currentIdx">1</span> / <span id="totalIdx">0</span></div>
    </div>
    <div class="viewer-nav next" id="nextBtn">→</div>
  </div>
</div>

<script>
// --- Gallery Logic ---
const galleryData = {gallery_json};
let currentCategory = Object.keys(galleryData)[0] || "Screenshots";
let currentIndex = 0;

const overlay = document.getElementById('viewerOverlay');
const viewerImg = document.getElementById('viewerImg');
const closeBtn = document.getElementById('closeViewer');
const openBtn = document.getElementById('openGallery');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const currentIdxSpan = document.getElementById('currentIdx');
const totalIdxSpan = document.getElementById('totalIdx');
const imageNameDiv = document.getElementById('imageName');

// Create Category Selector
if (Object.keys(galleryData).length > 1) {{
  const catSelector = document.createElement('div');
  catSelector.className = 'viewer-categories';
  Object.keys(galleryData).forEach(cat => {{
    const btn = document.createElement('button');
    btn.textContent = cat;
    btn.className = `cat-btn ${{cat === currentCategory ? 'active' : ''}}`;
    btn.onclick = () => switchCategory(cat);
    catSelector.appendChild(btn);
  }});
  overlay.appendChild(catSelector);
}}

function switchCategory(cat) {{
  currentCategory = cat;
  currentIndex = 0;
  const btns = document.querySelectorAll('.cat-btn');
  btns.forEach(b => b.classList.toggle('active', b.textContent === cat));
  updateViewer();
}}

function updateViewer() {{
  const images = galleryData[currentCategory];
  if (!images || images.length === 0) return;
  
  totalIdxSpan.textContent = images.length;
  currentIdxSpan.textContent = currentIndex + 1;
  
  const imgPath = images[currentIndex];
  const filename = imgPath.split('/').pop();
  if (imageNameDiv) imageNameDiv.textContent = filename;
  
  viewerImg.style.opacity = '0';
  viewerImg.src = encodeURI(imgPath);
  viewerImg.onload = () => {{ viewerImg.style.opacity = '1'; }};
}}

function nextImage() {{
  const images = galleryData[currentCategory];
  currentIndex = (currentIndex + 1) % images.length;
  updateViewer();
}}

function prevImage() {{
  const images = galleryData[currentCategory];
  currentIndex = (currentIndex - 1 + images.length) % images.length;
  updateViewer();
}}

openBtn.onclick = () => {{
  overlay.classList.add('active');
  document.body.style.overflow = 'hidden';
  updateViewer();
}};

closeBtn.onclick = () => {{
  overlay.classList.remove('active');
  document.body.style.overflow = '';
}};

overlay.onclick = (e) => {{ if (e.target === overlay) closeBtn.onclick(); }};
nextBtn.onclick = (e) => {{ e.stopPropagation(); nextImage(); }};
prevBtn.onclick = (e) => {{ e.stopPropagation(); prevImage(); }};

document.addEventListener('keydown', (e) => {{
  if (!overlay.classList.contains('active')) return;
  if (e.key === 'ArrowRight') nextImage();
  if (e.key === 'ArrowLeft') prevImage();
  if (e.key === 'Escape') closeBtn.onclick();
}});

// --- Utility: Escape HTML ---
function escapeHTML(str) {{
  return str.replace(/[&<>"']/g, function(m) {{
    return {{ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }}[m];
  }});
}}

// Search logic
const searchInput = document.getElementById('searchInput');
const allCards = document.querySelectorAll('.sign-card');
const allSections = document.querySelectorAll('.sign-section');

searchInput.addEventListener('input', () => {{
  const q = searchInput.value.toLowerCase().trim();
  
  allCards.forEach(card => {{
    const text = card.textContent.toLowerCase();
    card.style.display = text.includes(q) ? '' : 'none';
  }});
  
  allSections.forEach(section => {{
    const visibleCards = section.querySelectorAll('.sign-card:not([style*="display: none"])');
    section.style.display = visibleCards.length > 0 ? '' : 'none';
  }});
}});

// Expand cards logic
allCards.forEach(card => {{
  card.addEventListener('click', () => {{
    card.classList.toggle('expanded');
  }});
}});

// Sticky nav + active links
const navLinks = document.querySelectorAll('.nav-link');
window.addEventListener('scroll', () => {{
  let current = "";
  allSections.forEach(section => {{
    const sectionTop = section.offsetTop;
    if (pageYOffset >= sectionTop - 150) {{
      current = section.getAttribute("id");
    }}
  }});
  
  navLinks.forEach(link => {{
    link.classList.remove("active");
    if (link.getAttribute("href").includes(current)) {{
      link.classList.add("active");
    }}
  }});
}});

// Card Mouse Glow Effect (WOW Factor)
document.addEventListener('mousemove', e => {{
  allCards.forEach(card => {{
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    card.style.setProperty('--mouse-x', `${{x}}px`);
    card.style.setProperty('--mouse-y', `${{y}}px`);
  }});
}});
</script>

</body>
</html>"""

def main():
    base_path = "/Users/estai/Desktop/pdd"
    try:
        with open(f"{base_path}/wiki_signs.json", "r", encoding="utf-8") as f:
            sections = json.load(f)
    except FileNotFoundError:
        sections = []

    gallery_data = get_images(f"{base_path}/images")
    html = generate_html(sections, gallery_data)
    
    with open(f"{base_path}/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"Generated Premium index.html with {sum(len(v) for v in gallery_data.values())} gallery images.")

if __name__ == "__main__":
    main()
