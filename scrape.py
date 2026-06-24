#!/usr/bin/env python3
"""MPC Sample Manual - Mobile Web App Builder
AKAIのオンラインマニュアルをスマホ対応SPAとして生成します。
"""

import urllib.request
import urllib.error
import json
import time
import re
import sys
import os

BASE_URL = "https://www.akaipro.com/guides/mpc-sample/"
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "index.html")

NAV = [
    {"id": "introduction", "title": "Introduction", "url": "introduction.htm", "children": []},
    {"id": "setup", "title": "Setup", "url": "setup.htm", "children": [
        {"id": "firmware_updates", "title": "Firmware Updates", "url": "firmware_updates.htm", "children": []},
        {"id": "connection_diagram", "title": "Connection Diagram", "url": "connection_diagram.htm", "children": []},
    ]},
    {"id": "tutorial", "title": "Tutorial", "url": "tutorial.htm", "children": []},
    {"id": "features", "title": "Features", "url": "features.htm", "children": []},
    {"id": "operation", "title": "Operation", "url": "operation.htm", "children": [
        {"id": "sample_mode", "title": "Sample Mode", "url": "sample_mode.htm", "children": [
            {"id": "pad_play", "title": "Pad Play", "url": "pad_play.htm", "children": []},
            {"id": "loading_and_saving_samples", "title": "Loading & Saving Samples", "url": "loading_and_saving_samples.htm", "children": []},
        ]},
        {"id": "sample_record_mode", "title": "Sample Record Mode", "url": "sample_record_mode.htm", "children": []},
        {"id": "sequence_mode", "title": "Sequence Mode", "url": "sequence_mode.htm", "children": [
            {"id": "recording_sequences", "title": "Recording Sequences", "url": "recording_sequences.htm", "children": []},
            {"id": "editing_sequences", "title": "Editing Sequences", "url": "editing_sequences.htm", "children": []},
            {"id": "step_edit", "title": "Step Edit", "url": "step_edit.htm", "children": []},
            {"id": "song_mode", "title": "Song Mode", "url": "song_mode.htm", "children": []},
        ]},
        {"id": "effects", "title": "Effects", "url": "effects.htm", "children": [
            {"id": "pad_fx", "title": "Pad FX", "url": "pad_fx.htm", "children": []},
            {"id": "flex_beat", "title": "Flex Beat", "url": "flex_beat.htm", "children": []},
            {"id": "knob_fx", "title": "Knob FX", "url": "knob_fx.htm", "children": []},
            {"id": "compressor", "title": "Compressor", "url": "compressor.htm", "children": []},
        ]},
        {"id": "menus", "title": "Menus", "url": "menus.htm", "children": [
            {"id": "input_configuration", "title": "Input Configuration", "url": "input_configuration.htm", "children": []},
            {"id": "fader", "title": "Fader", "url": "fader.htm", "children": []},
            {"id": "time_correct", "title": "Time Correct", "url": "time_correct.htm", "children": []},
            {"id": "midi_configuration", "title": "MIDI Configuration", "url": "midi_configuration.htm", "children": []},
            {"id": "project", "title": "Project", "url": "project.htm", "children": []},
        ]},
    ]},
    {"id": "technical_specifications", "title": "Technical Specifications", "url": "technical_specifications.htm", "children": []},
    {"id": "trademarks___licenses", "title": "Trademarks & Licenses", "url": "trademarks___licenses.htm", "children": []},
]

def flatten(nav, result=None):
    if result is None:
        result = []
    for item in nav:
        result.append(item)
        flatten(item["children"], result)
    return result

FLAT = flatten(NAV)

def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return None

def remove_tag(html, tag):
    return re.sub(f"<{tag}[^>]*>.*?</{tag}>", "", html, flags=re.DOTALL | re.IGNORECASE)

def extract_content(html):
    """AKAIマニュアルページからメインコンテンツを抽出する。"""

    # まず不要なタグを削除
    for tag in ["script", "style", "noscript"]:
        html = remove_tag(html, tag)

    # Strategy 1: <main> または <article> タグ
    for tag in ["main", "article"]:
        m = re.search(f"<{tag}[^>]*>(.*?)</{tag}>", html, re.DOTALL | re.IGNORECASE)
        if m and len(m.group(1).strip()) > 300:
            return clean(m.group(1))

    # Strategy 2: id/class に "content" を含む div
    for pat in [
        r'<div[^>]+id="[^"]*content[^"]*"[^>]*>(.*?)</div\s*>',
        r'<div[^>]+class="[^"]*content[^"]*"[^>]*>(.*?)</div\s*>',
        r'<div[^>]+class="[^"]*chapter[^"]*"[^>]*>(.*?)</div\s*>',
        r'<div[^>]+class="[^"]*body[^"]*"[^>]*>(.*?)</div\s*>',
    ]:
        m = re.search(pat, html, re.DOTALL | re.IGNORECASE)
        if m and len(m.group(1).strip()) > 300:
            return clean(m.group(1))

    # Strategy 3: body 全体からナビを除去
    body = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL | re.IGNORECASE)
    if body:
        content = body.group(1)
        for tag in ["nav", "header", "footer", "aside"]:
            content = remove_tag(content, tag)
        # class に nav/menu/sidebar を含む div を除去
        content = re.sub(
            r'<div[^>]+(?:class|id)="[^"]*(?:nav|menu|sidebar|breadcrumb|header|footer)[^"]*"[^>]*>.*?</div>',
            "", content, flags=re.DOTALL | re.IGNORECASE
        )
        if len(content.strip()) > 100:
            return clean(content)

    return "<p><em>コンテンツを取得できませんでした。</em></p>"

def clean(content):
    """コンテンツのクリーニングと相対URLの修正。"""
    # 相対パスの画像URLを絶対URLに変換
    content = re.sub(
        r'(src=")(?!https?://)([^"]+)"',
        lambda m: f'{m.group(1)}{BASE_URL}{m.group(2)}"',
        content
    )
    # 内部リンクをdata属性に変換（JSで処理）
    content = re.sub(
        r'href="([^"#]+\.htm[^"]*)"',
        lambda m: f'href="javascript:void(0)" data-page="{m.group(1)}"',
        content
    )
    # akaipro.com への外部リンクはそのまま
    content = re.sub(
        r'href="(https?://[^"]+)"',
        r'href="\1" target="_blank" rel="noopener"',
        content
    )
    # テーブル要素のインラインstyle（固定px幅）を除去してモバイル対応に
    content = re.sub(
        r'(<(?:table|col|colgroup|tr|td|th)(?:\s[^>]*)?)\s+style="[^"]*"',
        r'\1', content
    )
    # colgroup/col タグを除去（幅指定のみで不要）
    content = re.sub(r'<colgroup\b[^>]*>.*?</colgroup>', '', content, flags=re.DOTALL | re.IGNORECASE)
    # 非改行スペースだけの空div/pを除去
    content = re.sub(r'<(?:div|p)[^>]*>\s*(?:&(?:nbsp|#160);|\s)*\s*</(?:div|p)>', '', content)
    # 画像の固定幅height属性を除去（CSS max-width:100% が効くように）
    content = re.sub(r'\s+(?:width|height)="[^"]*"', '', content)
    # 画像インラインstyleの固定幅を除去
    content = re.sub(
        r'(<img\b[^>]*)\s+style="[^"]*"',
        r'\1', content
    )
    return content.strip()

def build_html(pages_data):
    pages_json = json.dumps(pages_data, ensure_ascii=False)
    nav_json = json.dumps(NAV, ensure_ascii=False)
    flat_json = json.dumps(
        [{"id": p["id"], "title": p["title"], "url": p["url"]} for p in FLAT],
        ensure_ascii=False
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
<meta name="theme-color" content="#0f0f0f">
<title>MPC Sample User Guide</title>
<style>
:root {{
  --red: #e8002d;
  --red-dark: #b8001f;
  --bg: #111;
  --surface: #1c1c1c;
  --surface2: #272727;
  --surface3: #303030;
  --text: #e4e4e4;
  --text-muted: #888;
  --text-faint: #555;
  --border: #333;
  --sidebar-w: 260px;
  --header-h: 52px;
  --bottom-nav-h: 64px;
  --radius: 8px;
  --transition: 0.25s cubic-bezier(.4,0,.2,1);
}}
*,*::before,*::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ font-size: 16px; -webkit-text-size-adjust: 100%; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.7;
  height: 100dvh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}}

/* ─── Header ─────────────────────────────── */
.header {{
  height: var(--header-h);
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  padding: 0 12px;
  gap: 8px;
  flex-shrink: 0;
  position: relative;
  z-index: 20;
}}
.menu-btn {{
  width: 40px; height: 40px;
  display: flex; align-items: center; justify-content: center;
  border: none; background: transparent; color: var(--text);
  cursor: pointer; border-radius: var(--radius);
  font-size: 20px; flex-shrink: 0;
  transition: background var(--transition);
}}
.menu-btn:hover {{ background: var(--surface3); }}
.header-title {{
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}}
.header-logo {{
  width: 28px; height: 28px;
  background: var(--red);
  border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 900; color: #fff;
  flex-shrink: 0; letter-spacing: -0.5px;
}}
.header-text {{
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}
.search-btn {{
  width: 40px; height: 40px;
  display: flex; align-items: center; justify-content: center;
  border: none; background: transparent; color: var(--text-muted);
  cursor: pointer; border-radius: var(--radius);
  font-size: 18px; flex-shrink: 0;
  transition: color var(--transition), background var(--transition);
}}
.search-btn:hover {{ color: var(--text); background: var(--surface3); }}

/* ─── Body layout ─────────────────────────── */
.body {{
  display: flex;
  flex: 1;
  overflow: hidden;
  position: relative;
}}

/* ─── Sidebar overlay (mobile) ────────────── */
.overlay {{
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.6);
  z-index: 30;
}}
.overlay.active {{ display: block; }}

/* ─── Sidebar ─────────────────────────────── */
.sidebar {{
  width: var(--sidebar-w);
  background: var(--surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  flex-shrink: 0;
  transition: transform var(--transition);
  z-index: 40;
}}
.sidebar-inner {{
  overflow-y: auto;
  flex: 1;
  padding: 8px 0 16px;
  overscroll-behavior: contain;
  -webkit-overflow-scrolling: touch;
}}
.sidebar-inner::-webkit-scrollbar {{ width: 4px; }}
.sidebar-inner::-webkit-scrollbar-track {{ background: transparent; }}
.sidebar-inner::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 2px; }}

/* Nav items */
.nav-section {{ padding: 8px 0 0; }}
.nav-item {{
  display: flex;
  align-items: center;
  padding: 9px 16px 9px 16px;
  cursor: pointer;
  color: var(--text-muted);
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 0;
  transition: background var(--transition), color var(--transition);
  line-height: 1.3;
  gap: 8px;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}}
.nav-item:hover {{ background: var(--surface2); color: var(--text); }}
.nav-item.active {{ background: var(--surface3); color: var(--red); font-weight: 600; }}
.nav-item.active::before {{
  content: '';
  position: absolute;
  left: 0;
  width: 3px;
  height: 32px;
  background: var(--red);
  border-radius: 0 2px 2px 0;
}}
.nav-item {{ position: relative; }}
.nav-caret {{
  margin-left: auto;
  font-size: 10px;
  color: var(--text-faint);
  transition: transform var(--transition);
  flex-shrink: 0;
}}
.nav-item.open .nav-caret {{ transform: rotate(90deg); }}
.nav-children {{
  overflow: hidden;
  max-height: 0;
  transition: max-height 0.3s ease;
}}
.nav-children.open {{ max-height: 500px; }}
.nav-item.child {{ padding-left: 32px; font-size: 0.82rem; font-weight: 400; }}
.nav-item.grandchild {{ padding-left: 48px; font-size: 0.8rem; }}

/* ─── Content area ────────────────────────── */
.content-area {{
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
  display: flex;
  flex-direction: column;
}}
.content-wrap {{
  flex: 1;
  padding: 28px 24px 120px;
  max-width: 860px;
  width: 100%;
  margin: 0 auto;
}}

/* ─── Page content typography ─────────────── */
.page-content h1 {{
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--red);
  line-height: 1.3;
}}
.page-content h2 {{
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text);
  margin: 28px 0 12px;
  padding-left: 12px;
  border-left: 3px solid var(--red);
}}
.page-content h3 {{
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--text);
  margin: 20px 0 8px;
}}
.page-content h4, .page-content h5, .page-content h6 {{
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-muted);
  margin: 16px 0 6px;
}}
.page-content p {{
  margin-bottom: 14px;
  color: var(--text);
}}
.page-content ul, .page-content ol {{
  margin: 8px 0 16px 24px;
  color: var(--text);
}}
.page-content li {{ margin-bottom: 6px; }}
.page-content img {{
  max-width: 100%;
  height: auto;
  border-radius: var(--radius);
  margin: 12px 0;
  display: block;
}}
/* テーブル：モバイルで横スクロール */
.table-wrap {{
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  margin: 16px 0;
  border-radius: var(--radius);
  border: 1px solid var(--border);
}}
.page-content table {{
  width: 100%;
  min-width: max-content;
  border-collapse: collapse;
  font-size: 0.85rem;
}}
.page-content table thead tr {{
  background: var(--surface3);
}}
.page-content th, .page-content td {{
  padding: 9px 14px;
  border: 1px solid var(--border);
  text-align: left;
  vertical-align: top;
  white-space: nowrap;
}}
.page-content td {{ white-space: normal; min-width: 80px; }}
.page-content th {{ font-weight: 600; color: var(--text); white-space: nowrap; }}
.page-content td {{ color: var(--text-muted); }}
/* AKAI固有クラスのスタイル */
.description_on_page {{ }}
.page-content .p {{ margin-bottom: 8px; line-height: 1.7; }}
.page-content .p.h1 {{ margin: 0 0 20px; }}
.page-content span {{ color: inherit; }}
.page-content .ic {{ display: inline; }}
.page-content a {{
  color: var(--red);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color var(--transition);
}}
.page-content a:hover {{ border-bottom-color: var(--red); }}
.page-content strong, .page-content b {{ color: var(--text); font-weight: 600; }}
.page-content em, .page-content i {{ color: var(--text-muted); font-style: italic; }}
.page-content code {{
  background: var(--surface3);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.875em;
}}
.page-content blockquote {{
  border-left: 3px solid var(--red);
  margin: 16px 0;
  padding: 12px 16px;
  background: var(--surface2);
  border-radius: 0 var(--radius) var(--radius) 0;
  color: var(--text-muted);
}}
.page-content hr {{
  border: none;
  border-top: 1px solid var(--border);
  margin: 24px 0;
}}

/* ─── Loading ─────────────────────────────── */
.loading {{
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--text-muted);
  gap: 12px;
}}
.spinner {{
  width: 24px; height: 24px;
  border: 2px solid var(--border);
  border-top-color: var(--red);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}

/* ─── Page navigation ─────────────────────── */
.page-nav {{
  display: flex;
  gap: 12px;
  padding: 20px 0 8px;
  border-top: 1px solid var(--border);
  margin-top: 32px;
}}
.page-nav-btn {{
  flex: 1;
  padding: 14px 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text-muted);
  cursor: pointer;
  text-align: center;
  transition: all var(--transition);
  font-size: 0.875rem;
  line-height: 1.3;
  -webkit-tap-highlight-color: transparent;
}}
.page-nav-btn:hover:not(:disabled) {{
  background: var(--surface2);
  border-color: var(--red);
  color: var(--text);
}}
.page-nav-btn:disabled {{ opacity: 0.3; cursor: default; }}
.page-nav-btn .nav-label {{ font-size: 0.75rem; color: var(--text-faint); margin-bottom: 4px; }}
.page-nav-btn .nav-title {{ font-weight: 500; color: var(--text); }}
.page-nav-btn.prev {{ text-align: left; }}
.page-nav-btn.next {{ text-align: right; }}
.page-nav-btn.prev::before {{ content: '←  '; }}
.page-nav-btn.next::after {{ content: '  →'; }}

/* ─── Search overlay ──────────────────────── */
.search-overlay {{
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.8);
  z-index: 50;
  align-items: flex-start;
  justify-content: center;
  padding-top: 80px;
}}
.search-overlay.active {{ display: flex; }}
.search-box {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  width: min(90vw, 560px);
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0,0,0,.6);
}}
.search-input-wrap {{
  display: flex;
  align-items: center;
  padding: 0 16px;
  border-bottom: 1px solid var(--border);
}}
.search-input-wrap span {{ color: var(--text-muted); font-size: 18px; }}
.search-input {{
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text);
  font-size: 1.1rem;
  padding: 16px 12px;
}}
.search-input::placeholder {{ color: var(--text-faint); }}
.search-results {{
  max-height: 400px;
  overflow-y: auto;
  padding: 8px;
}}
.search-result {{
  padding: 12px;
  cursor: pointer;
  border-radius: 6px;
  transition: background var(--transition);
}}
.search-result:hover {{ background: var(--surface2); }}
.search-result-title {{ font-weight: 600; color: var(--text); font-size: 0.9rem; }}
.search-result-excerpt {{ color: var(--text-muted); font-size: 0.8rem; margin-top: 4px; line-height: 1.5; }}
.search-result mark {{ background: rgba(232,0,45,.25); color: var(--red); border-radius: 2px; }}
.search-empty {{ padding: 24px; text-align: center; color: var(--text-faint); font-size: 0.9rem; }}
.search-close-btn {{
  padding: 4px 12px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 0.85rem;
  cursor: pointer;
  transition: color var(--transition);
}}
.search-close-btn:hover {{ color: var(--text); }}

/* ─── Breadcrumb ──────────────────────────── */
.breadcrumb {{
  font-size: 0.78rem;
  color: var(--text-faint);
  margin-bottom: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}}
.breadcrumb span {{ color: var(--text-faint); }}
.breadcrumb a {{
  color: var(--text-muted);
  cursor: pointer;
  text-decoration: none;
  transition: color var(--transition);
}}
.breadcrumb a:hover {{ color: var(--red); }}

/* ─── Responsive ──────────────────────────── */
@media (max-width: 767px) {{
  .sidebar {{
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
    transform: translateX(-100%);
    box-shadow: 4px 0 20px rgba(0,0,0,.4);
  }}
  .sidebar.open {{ transform: translateX(0); }}
  .content-wrap {{
    padding: 20px 16px 100px;
  }}
  .page-content h1 {{ font-size: 1.4rem; }}
  .page-content h2 {{ font-size: 1.1rem; }}
  .page-nav {{
    flex-direction: column;
    gap: 8px;
  }}
  .page-nav-btn {{ text-align: left !important; }}
  .page-nav-btn.next::after {{ display: none; }}
  .page-nav-btn.prev::before {{ display: none; }}
  .page-nav-btn.prev::after {{ content: none; }}
}}
@media (min-width: 768px) {{
  .menu-btn {{ display: none; }}
  .overlay {{ display: none !important; }}
}}
</style>
</head>
<body>

<!-- Header -->
<header class="header">
  <button class="menu-btn" id="menuBtn" aria-label="Toggle menu">&#9776;</button>
  <div class="header-title">
    <div class="header-logo">MPC</div>
    <span class="header-text">MPC Sample User Guide</span>
  </div>
  <button class="search-btn" id="searchBtn" aria-label="Search" title="Search (/)">&#128269;</button>
</header>

<!-- Body -->
<div class="body">
  <!-- Overlay for mobile sidebar -->
  <div class="overlay" id="overlay"></div>

  <!-- Sidebar -->
  <nav class="sidebar" id="sidebar" aria-label="Table of contents">
    <div class="sidebar-inner" id="sidebarInner"></div>
  </nav>

  <!-- Content -->
  <main class="content-area" id="contentArea">
    <div class="content-wrap">
      <div id="breadcrumb" class="breadcrumb"></div>
      <div class="page-content" id="pageContent">
        <div class="loading"><div class="spinner"></div> Loading...</div>
      </div>
      <div class="page-nav" id="pageNav"></div>
    </div>
  </main>
</div>

<!-- Search overlay -->
<div class="search-overlay" id="searchOverlay" role="dialog" aria-modal="true" aria-label="Search">
  <div class="search-box">
    <div class="search-input-wrap">
      <span>&#128269;</span>
      <input type="search" class="search-input" id="searchInput" placeholder="Search manual..." autocomplete="off" spellcheck="false">
      <button class="search-close-btn" id="searchClose">Close</button>
    </div>
    <div class="search-results" id="searchResults"></div>
  </div>
</div>

<script>
const PAGES = {pages_json};
const NAV = {nav_json};
const FLAT = {flat_json};

// ── State ───────────────────────────────────
let currentId = null;

// ── Build flat index for search ─────────────
const searchIndex = FLAT.map(item => {{
  const raw = PAGES[item.id] || '';
  const text = raw.replace(/<[^>]+>/g, ' ').replace(/\\s+/g, ' ').trim();
  return {{ id: item.id, title: item.title, text }};
}});

// ── Navigation helpers ──────────────────────
function getParents(id, nav, path) {{
  for (const item of nav) {{
    if (item.id === id) return [...path, item];
    if (item.children.length) {{
      const found = getParents(id, item.children, [...path, item]);
      if (found) return found;
    }}
  }}
  return null;
}}

function getNeighbors(id) {{
  const idx = FLAT.findIndex(p => p.id === id);
  return {{
    prev: idx > 0 ? FLAT[idx - 1] : null,
    next: idx < FLAT.length - 1 ? FLAT[idx + 1] : null,
  }};
}}

// ── Sidebar rendering ───────────────────────
function renderNav(items, depth, parentId) {{
  return items.map(item => {{
    const hasChildren = item.children && item.children.length > 0;
    const cls = depth === 0 ? 'nav-item' : depth === 1 ? 'nav-item child' : 'nav-item grandchild';
    const caret = hasChildren ? '<span class="nav-caret">&#9654;</span>' : '';
    let html = `<div class="${{cls}}" data-id="${{item.id}}" role="button" tabindex="0">${{item.title}}${{caret}}</div>`;
    if (hasChildren) {{
      html += `<div class="nav-children" data-parent="${{item.id}}">${{renderNav(item.children, depth + 1, item.id)}}</div>`;
    }}
    return html;
  }}).join('');
}}

function initSidebar() {{
  document.getElementById('sidebarInner').innerHTML = renderNav(NAV, 0, null);

  document.querySelectorAll('.nav-item').forEach(el => {{
    el.addEventListener('click', () => navigateTo(el.dataset.id));
    el.addEventListener('keydown', e => {{ if (e.key === 'Enter') navigateTo(el.dataset.id); }});
  }});
}}

function updateSidebarActive(id) {{
  document.querySelectorAll('.nav-item').forEach(el => {{
    el.classList.remove('active', 'open');
  }});
  document.querySelectorAll('.nav-children').forEach(el => el.classList.remove('open'));

  const active = document.querySelector(`.nav-item[data-id="${{id}}"]`);
  if (active) {{
    active.classList.add('active');
    // Expand parent groups
    const parents = getParents(id, NAV, []);
    if (parents) {{
      parents.forEach(p => {{
        const el = document.querySelector(`.nav-item[data-id="${{p.id}}"]`);
        if (el) el.classList.add('open');
        const ch = document.querySelector(`.nav-children[data-parent="${{p.id}}"]`);
        if (ch) ch.classList.add('open');
      }});
    }}
    // Scroll into view in sidebar
    setTimeout(() => {{
      active.scrollIntoView({{ block: 'nearest', behavior: 'smooth' }});
    }}, 100);
  }}
}}

// ── Page rendering ──────────────────────────
function navigateTo(id, pushState) {{
  if (!id || !PAGES[id]) return;
  currentId = id;

  // Update URL hash
  if (pushState !== false) {{
    history.pushState({{ id }}, '', '#' + id);
  }}

  // Scroll content to top
  document.getElementById('contentArea').scrollTo(0, 0);

  // Update sidebar
  updateSidebarActive(id);

  // Close mobile sidebar
  closeSidebar();

  // Render breadcrumb
  const parents = getParents(id, NAV, []) || [];
  const crumbEl = document.getElementById('breadcrumb');
  if (parents.length > 1) {{
    crumbEl.innerHTML = parents.slice(0, -1).map(p =>
      `<a onclick="navigateTo('${{p.id}}')">${{p.title}}</a><span>/</span>`
    ).join('') + `<span>${{parents[parents.length - 1].title}}</span>`;
  }} else {{
    crumbEl.innerHTML = '';
  }}

  // Render content
  document.getElementById('pageContent').innerHTML = PAGES[id] || '<p>No content available.</p>';

  // テーブルをスクロール可能なラッパーで囲む（モバイル対応）
  document.querySelectorAll('#pageContent table').forEach(t => {{
    if (t.closest('.table-wrap')) return;
    const wrap = document.createElement('div');
    wrap.className = 'table-wrap';
    t.parentNode.insertBefore(wrap, t);
    wrap.appendChild(t);
    t.removeAttribute('style');
  }});

  // 内部リンクのクリックハンドラ
  document.querySelectorAll('#pageContent [data-page]').forEach(a => {{
    a.addEventListener('click', e => {{
      e.preventDefault();
      const target = a.dataset.page;
      const matched = FLAT.find(p => p.url === target || p.id === target);
      if (matched) navigateTo(matched.id);
    }});
  }});

  // Render prev/next navigation
  const {{ prev, next }} = getNeighbors(id);
  const navEl = document.getElementById('pageNav');
  navEl.innerHTML = `
    <button class="page-nav-btn prev" ${{!prev ? 'disabled' : ''}} onclick="navigateTo('${{prev?.id}}')">
      ${{prev ? `<div class="nav-label">Previous</div><div class="nav-title">${{prev.title}}</div>` : '—'}}
    </button>
    <button class="page-nav-btn next" ${{!next ? 'disabled' : ''}} onclick="navigateTo('${{next?.id}}')">
      ${{next ? `<div class="nav-label">Next</div><div class="nav-title">${{next.title}}</div>` : '—'}}
    </button>
  `;
}}

// ── Mobile sidebar ──────────────────────────
function openSidebar() {{
  document.getElementById('sidebar').classList.add('open');
  document.getElementById('overlay').classList.add('active');
  document.body.style.overflow = 'hidden';
}}
function closeSidebar() {{
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('overlay').classList.remove('active');
  document.body.style.overflow = '';
}}

// ── Search ──────────────────────────────────
let searchTimer = null;
function openSearch() {{
  document.getElementById('searchOverlay').classList.add('active');
  document.getElementById('searchInput').focus();
}}
function closeSearch() {{
  document.getElementById('searchOverlay').classList.remove('active');
  document.getElementById('searchInput').value = '';
  document.getElementById('searchResults').innerHTML = '';
}}
function doSearch(q) {{
  const el = document.getElementById('searchResults');
  if (!q || q.length < 2) {{ el.innerHTML = ''; return; }}
  const results = [];
  const re = new RegExp(q.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&'), 'gi');
  for (const item of searchIndex) {{
    const ti = item.title.match(re);
    const tx = item.text.match(re);
    if (!ti && !tx) continue;
    // Find excerpt
    let excerpt = '';
    const pos = item.text.search(re);
    if (pos >= 0) {{
      const start = Math.max(0, pos - 60);
      const end = Math.min(item.text.length, pos + 120);
      excerpt = (start > 0 ? '…' : '') + item.text.slice(start, end).replace(re, m => `<mark>${{m}}</mark>`) + (end < item.text.length ? '…' : '');
    }}
    const titleHl = item.title.replace(re, m => `<mark>${{m}}</mark>`);
    results.push({{ item, titleHl, excerpt, score: ti ? 2 : 1 }});
    if (results.length >= 12) break;
  }}
  if (!results.length) {{
    el.innerHTML = '<div class="search-empty">No results found.</div>';
    return;
  }}
  el.innerHTML = results.map(r => `
    <div class="search-result" data-id="${{r.item.id}}">
      <div class="search-result-title">${{r.titleHl}}</div>
      ${{r.excerpt ? `<div class="search-result-excerpt">${{r.excerpt}}</div>` : ''}}
    </div>
  `).join('');
  el.querySelectorAll('.search-result').forEach(el => {{
    el.addEventListener('click', () => {{
      navigateTo(el.dataset.id);
      closeSearch();
    }});
  }});
}}

// ── Events ──────────────────────────────────
document.getElementById('menuBtn').addEventListener('click', () => {{
  document.getElementById('sidebar').classList.contains('open') ? closeSidebar() : openSidebar();
}});
document.getElementById('overlay').addEventListener('click', closeSidebar);
document.getElementById('searchBtn').addEventListener('click', openSearch);
document.getElementById('searchClose').addEventListener('click', closeSearch);
document.getElementById('searchInput').addEventListener('input', e => {{
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => doSearch(e.target.value.trim()), 200);
}});
document.getElementById('searchOverlay').addEventListener('click', e => {{
  if (e.target === e.currentTarget) closeSearch();
}});

// Keyboard shortcuts
document.addEventListener('keydown', e => {{
  if (e.key === '/' && !e.ctrlKey && !e.metaKey && document.activeElement.tagName !== 'INPUT') {{
    e.preventDefault(); openSearch();
  }}
  if (e.key === 'Escape') closeSearch();
  if (e.key === 'ArrowLeft' && !e.ctrlKey) {{
    const {{ prev }} = getNeighbors(currentId);
    if (prev) navigateTo(prev.id);
  }}
  if (e.key === 'ArrowRight' && !e.ctrlKey) {{
    const {{ next }} = getNeighbors(currentId);
    if (next) navigateTo(next.id);
  }}
}});

// Browser back/forward
window.addEventListener('popstate', e => {{
  if (e.state?.id) navigateTo(e.state.id, false);
}});

// ── Init ─────────────────────────────────────
initSidebar();
const initId = location.hash.slice(1) || FLAT[0]?.id;
navigateTo(initId, false);
history.replaceState({{ id: initId }}, '', '#' + initId);
</script>
</body>
</html>"""

# ── Main ──────────────────────────────────────
def main():
    print("MPC Sample User Guide - Web App Builder")
    print("=" * 50)
    print(f"Fetching {len(FLAT)} pages...\n")

    pages_data = {}
    failed = []

    for i, item in enumerate(FLAT, 1):
        url = BASE_URL + item["url"]
        print(f"[{i:2}/{len(FLAT)}] {item['title']}... ", end="", flush=True)
        html = fetch(url)
        if html:
            content = extract_content(html)
            pages_data[item["id"]] = content
            print(f"OK  ({len(content):,} chars)")
        else:
            pages_data[item["id"]] = f"<p><em>Failed to load: {item['title']}</em></p>"
            failed.append(item["title"])
            print("FAILED")
        if i < len(FLAT):
            time.sleep(0.4)

    print(f"\nBuilding HTML...")
    output = build_html(pages_data)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(output)

    size_kb = len(output.encode("utf-8")) / 1024
    print(f"Output: {OUTPUT_FILE}")
    print(f"Size:   {size_kb:.0f} KB")
    if failed:
        print(f"Failed: {', '.join(failed)}")
    print("\nDone! Open index.html in a browser.")

if __name__ == "__main__":
    main()
