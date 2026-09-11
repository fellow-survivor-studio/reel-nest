from __future__ import annotations

import html
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
DIST = ROOT / "dist"

LANGUAGES = {
    "ko": {"name": "한국어", "html_lang": "ko", "description": "Reel Nest 개인정보처리방침"},
    "en": {"name": "English", "html_lang": "en", "description": "Reel Nest Privacy Policy"},
    "ja": {"name": "日本語", "html_lang": "ja", "description": "Reel Nest プライバシーポリシー"},
    "zh": {"name": "中文", "html_lang": "zh-CN", "description": "Reel Nest 隐私政策"},
    "es": {"name": "Español", "html_lang": "es", "description": "Política de privacidad de Reel Nest"},
    "pt": {"name": "Português", "html_lang": "pt-BR", "description": "Política de Privacidade do Reel Nest"},
}

LABELS = {
    "ko": {"brand": "개인정보 보호", "language": "언어", "toc": "목차", "top": "맨 위로", "updated": "정책 시행일", "skip": "본문으로 건너뛰기"},
    "en": {"brand": "Privacy", "language": "Language", "toc": "Contents", "top": "Back to top", "updated": "Effective date", "skip": "Skip to content"},
    "ja": {"brand": "プライバシー", "language": "言語", "toc": "目次", "top": "ページ上部へ", "updated": "施行日", "skip": "本文へ移動"},
    "zh": {"brand": "隐私", "language": "语言", "toc": "目录", "top": "返回顶部", "updated": "生效日期", "skip": "跳到正文"},
    "es": {"brand": "Privacidad", "language": "Idioma", "toc": "Contenido", "top": "Volver arriba", "updated": "Fecha de vigencia", "skip": "Saltar al contenido"},
    "pt": {"brand": "Privacidade", "language": "Idioma", "toc": "Conteúdo", "top": "Voltar ao topo", "updated": "Data de vigência", "skip": "Ir para o conteúdo"},
}

BASE_URL = "https://fellow-survivor-studio.github.io/reel-nest/"
URL_RE = re.compile(r"^https://[^\s]+$")
SECTION_RE = re.compile(r"^(\d+)\.\s+(.+)$")
SUBSECTION_RE = re.compile(r"^(?:[AB]|[가나다라마바사아자차카타파하])\.\s*(.+)$")


def page_href(current: str, target: str) -> str:
    prefix = "" if current == "ko" else "../"
    return prefix if target == "ko" else f"{prefix}{target}/"


def slug(number: str) -> str:
    return f"section-{number}"


def render_document(text: str) -> tuple[str, str, list[tuple[str, str]]]:
    lines = [line.strip() for line in text.replace("\r\n", "\n").split("\n")]
    title = lines[0]
    effective = next((line for line in lines[1:] if line), "")
    body: list[str] = []
    toc: list[tuple[str, str]] = []
    in_list = False
    skipped_effective = False

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            body.append("</ul>")
            in_list = False

    for line in lines[1:]:
        if not line:
            close_list()
            continue
        if not skipped_effective and line == effective:
            skipped_effective = True
            continue
        section = SECTION_RE.match(line)
        if section:
            close_list()
            section_id = slug(section.group(1))
            toc.append((section_id, line))
            body.append(f'<h2 id="{section_id}">{html.escape(line)}</h2>')
            continue
        subsection = SUBSECTION_RE.match(line)
        if subsection:
            close_list()
            body.append(f"<h3>{html.escape(line)}</h3>")
            continue
        if line.startswith("- "):
            if not in_list:
                body.append("<ul>")
                in_list = True
            body.append(f"<li>{html.escape(line[2:])}</li>")
            continue
        close_list()
        if URL_RE.match(line):
            safe_url = html.escape(line, quote=True)
            body.append(f'<p class="external-link"><a href="{safe_url}" rel="noopener noreferrer">{safe_url}</a></p>')
        else:
            body.append(f"<p>{html.escape(line)}</p>")
    close_list()
    return title, effective, toc, body


def render_page(lang: str, text: str) -> str:
    meta = LANGUAGES[lang]
    labels = LABELS[lang]
    title, effective, toc, body = render_document(text)
    css_href = "styles.css" if lang == "ko" else "../styles.css"
    canonical = BASE_URL if lang == "ko" else f"{BASE_URL}{lang}/"
    language_items = []
    for code, item in LANGUAGES.items():
        current = ' aria-current="page"' if code == lang else ""
        language_items.append(
            f'<a href="{page_href(lang, code)}" lang="{item["html_lang"]}"{current}>'
            f'{html.escape(item["name"])}</a>'
        )
    language_links = "".join(language_items)
    alternate_links = "\n".join(
        f'<link rel="alternate" hreflang="{item["html_lang"]}" href="{BASE_URL if code == "ko" else BASE_URL + code + "/"}">'
        for code, item in LANGUAGES.items()
    )
    toc_links = "".join(f'<li><a href="#{anchor}">{html.escape(label)}</a></li>' for anchor, label in toc)
    effective_value = re.sub(r"^[^:：]+[:：]\s*", "", effective)
    return f'''<!doctype html>
<html lang="{meta["html_lang"]}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{html.escape(meta["description"], quote=True)}">
  <meta name="theme-color" content="#13263f">
  <meta name="robots" content="index, follow">
  <title>{html.escape(title)}</title>
  <link rel="canonical" href="{canonical}">
  {alternate_links}
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='16' fill='%2313263f'/%3E%3Cpath d='M18 18h28v8H27v8h16v8H27v4h19v8H18z' fill='%236dc5ff'/%3E%3C/svg%3E">
  <link rel="stylesheet" href="{css_href}">
</head>
<body>
  <a class="skip-link" href="#policy">{html.escape(labels["skip"])}</a>
  <header class="site-header">
    <a class="brand" href="{page_href(lang, "ko")}" aria-label="Reel Nest">
      <span class="brand-mark" aria-hidden="true">R</span>
      <span><strong>Reel Nest</strong><small>{html.escape(labels["brand"])}</small></span>
    </a>
    <nav class="languages" aria-label="{html.escape(labels["language"], quote=True)}">{language_links}</nav>
  </header>
  <main class="page-shell">
    <aside class="toc" aria-label="{html.escape(labels["toc"], quote=True)}">
      <span>{html.escape(labels["toc"])}</span>
      <ol>{toc_links}</ol>
    </aside>
    <article id="policy" class="policy-card">
      <div class="document-heading">
        <p class="eyebrow">Reel Nest · {html.escape(labels["brand"])}</p>
        <h1>{html.escape(title)}</h1>
        <p class="effective"><span>{html.escape(labels["updated"])}</span>{html.escape(effective_value)}</p>
      </div>
      <div class="document-body">{''.join(body)}</div>
      <a class="back-to-top" href="#">↑ {html.escape(labels["top"])}</a>
    </article>
  </main>
  <footer>© 2026 Fellow Survivor Studio · Reel Nest</footer>
</body>
</html>
'''


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copy2(ROOT / "styles.css", DIST / "styles.css")
    for lang in LANGUAGES:
        source = CONTENT / f"privacy_policy_{lang}.txt"
        if not source.exists():
            raise FileNotFoundError(source)
        output_dir = DIST if lang == "ko" else DIST / lang
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "index.html").write_text(render_page(lang, source.read_text(encoding="utf-8")), encoding="utf-8")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}sitemap.xml\n", encoding="utf-8")
    urls = [BASE_URL, *(f"{BASE_URL}{lang}/" for lang in LANGUAGES if lang != "ko")]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{url}</loc></url>\n" for url in urls) + "</urlset>\n"
    (DIST / "sitemap.xml").write_text(sitemap, encoding="utf-8")


if __name__ == "__main__":
    main()
