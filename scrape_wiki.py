#!/usr/bin/env python3
"""Scrape Kazakhstan road signs from Kazakh Wikipedia using MediaWiki API."""

import json
import re
import urllib.request
import urllib.parse
from html.parser import HTMLParser

WIKI_API = "https://kk.wikipedia.org/w/api.php"
# List of pages to scrape
PAGES = [
    "Қазақстан_жол_белгілері",
    "Жол_таңбалары",
    "Бағдаршам",
]

def get_page_html(title):
    """Fetch the parsed HTML of a Wikipedia article via API."""
    params = {
        "action": "parse",
        "page": title,
        "format": "json",
        "prop": "text",
        "utf8": "1",
    }
    url = f"{WIKI_API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "KZRoadSignsScraper/1.0 (educational project)"
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if "parse" in data:
            return data["parse"]["text"]["*"]
    except Exception as e:
        print(f"Error fetching {title}: {e}")
    return ""


class WikiTableParser(HTMLParser):
    """Parse Wikipedia HTML tables to extract road sign data."""

    def __init__(self):
        super().__init__()
        self.sections = []        # [{title, signs}]
        self.current_section = None
        self.current_sign = {}
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.cell_index = 0
        self.cell_content = ""
        self.tag_stack = []
        self.in_h2 = False
        self.in_h3 = False
        self.h_text = ""

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)
        self.tag_stack.append(tag)

        if tag == "h2":
            self.in_h2 = True
            self.h_text = ""
        elif tag == "h3":
            self.in_h3 = True
            self.h_text = ""

        if tag == "table" and "wikitable" in attrs_d.get("class", ""):
            self.in_table = True

        if self.in_table:
            if tag == "tr":
                self.in_row = True
                self.cell_index = 0
                self.current_sign = {}
            if tag in ("td", "th"):
                self.in_cell = True
                self.cell_content = ""
            if tag == "img" and self.in_cell:
                src = attrs_d.get("src", "")
                if src:
                    src = src.replace("//upload.", "https://upload.")
                    src = re.sub(r'/(\d+)px-', '/120px-', src)
                    if "src" not in self.current_sign:
                        self.current_sign["src"] = src

    def handle_endtag(self, tag):
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()

        if tag == "h2":
            self.in_h2 = False
            title = self.h_text.strip()
            if title and any(k in title.lower() for k in ["белгі", "белгілер", "тақтайша", "таңба", "таңбалау", "бағдаршам"]):
                self.current_section = {"title": title, "signs": []}
                self.sections.append(self.current_section)
        elif tag == "h3":
            self.in_h3 = False

        if self.in_table:
            if tag in ("td", "th"):
                self.in_cell = False
                content = self.cell_content.strip()
                content = re.sub(r'\s+', ' ', content)

                if self.cell_index == 0:
                    self.current_sign["number"] = content
                elif self.cell_index == 2:
                    self.current_sign["name"] = content
                elif self.cell_index == 3:
                    self.current_sign["description"] = content
                self.cell_index += 1

            if tag == "tr":
                self.in_row = False
                if self.current_sign.get("number") and self.current_sign.get("name"):
                    num = self.current_sign["number"]
                    if not any(k in num.lower() for k in ["белгі", "нөмір", "кескін", "аты", "түсіндіру", "таңба"]):
                        if self.current_section is not None:
                            self.current_section["signs"].append(self.current_sign.copy())
                self.current_sign = {}

            if tag == "table":
                self.in_table = False

    def handle_data(self, data):
        if self.in_h2 or self.in_h3:
            self.h_text += data
        if self.in_cell:
            self.cell_content += data


def main():
    all_sections = []
    
    for title in PAGES:
        print(f"Fetching {title} via API...")
        html = get_page_html(title)
        if not html:
            continue
            
        parser = WikiTableParser()
        parser.feed(html)
        
        print(f"  Found {len(parser.sections)} sections in {title}")
        all_sections.extend(parser.sections)

    # Filter out empty sections
    all_sections = [s for s in all_sections if s["signs"]]

    print(f"\nTotal sections: {len(all_sections)}")
    total_signs = sum(len(s["signs"]) for s in all_sections)
    print(f"Total signs/items: {total_signs}")

    # Save JSON
    with open("/Users/estai/Desktop/pdd/wiki_signs.json", "w", encoding="utf-8") as f:
        json.dump(all_sections, f, ensure_ascii=False, indent=2)
    print(f"\nSaved all data to wiki_signs.json")


if __name__ == "__main__":
    main()
