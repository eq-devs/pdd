#!/usr/bin/env python3
"""Generate the premium traffic signs website from wiki_signs.json data."""

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
            {"number": "1.2", "name": "Тік таңба", "description": "Жол құрылыстарының элементтеріне және жол жабдықтарына түсірілетін сызықтар мен таңбалар.", "src": "https://safety-driving.kz/upload/medialibrary/556/1ga83xj41rk3sktqmd40zgbxy1hgsagg/road_2.jpg"},
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

def generate_html(sections):
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

<script>
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
    try:
        with open("/Users/estai/Desktop/pdd/wiki_signs.json", "r", encoding="utf-8") as f:
            sections = json.load(f)
    except FileNotFoundError:
        sections = []

    html = generate_html(sections)
    with open("/Users/estai/Desktop/pdd/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"Generated Premium index.html ({len(html)} bytes)")

if __name__ == "__main__":
    main()
