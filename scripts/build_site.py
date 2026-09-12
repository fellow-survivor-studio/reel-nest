from __future__ import annotations

import html
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
DIST = ROOT / "dist"

LANGUAGES = {
    "ko": {"name": "한국어", "html_lang": "ko"},
    "en": {"name": "English", "html_lang": "en"},
    "ja": {"name": "日本語", "html_lang": "ja"},
    "zh": {"name": "中文", "html_lang": "zh-CN"},
    "es": {"name": "Español", "html_lang": "es"},
    "pt": {"name": "Português", "html_lang": "pt-BR"},
}

# Each document is published under its own path prefix: the privacy policy at the
# site root (kept for the URL already registered in Google Play) and the terms of
# use under terms/. Korean is served at the prefix itself, other languages below it.
DOCUMENTS = {
    "privacy": {"source": "privacy_policy", "prefix": ""},
    "terms": {"source": "terms_of_use", "prefix": "terms/"},
}

DESCRIPTIONS = {
    "privacy": {
        "ko": "Reel Nest 개인정보처리방침",
        "en": "Reel Nest Privacy Policy",
        "ja": "Reel Nest プライバシーポリシー",
        "zh": "Reel Nest 隐私政策",
        "es": "Política de privacidad de Reel Nest",
        "pt": "Política de Privacidade do Reel Nest",
    },
    "terms": {
        "ko": "Reel Nest 이용약관",
        "en": "Reel Nest Terms of Use",
        "ja": "Reel Nest 利用規約",
        "zh": "Reel Nest 使用条款",
        "es": "Términos de Uso de Reel Nest",
        "pt": "Termos de Uso do Reel Nest",
    },
}

LABELS = {
    "ko": {"privacy": "개인정보 보호", "terms": "이용약관", "privacy_link": "개인정보처리방침", "language": "언어", "toc": "목차", "top": "맨 위로", "updated": "시행일", "skip": "본문으로 건너뛰기"},
    "en": {"privacy": "Privacy", "terms": "Terms", "privacy_link": "Privacy Policy", "language": "Language", "toc": "Contents", "top": "Back to top", "updated": "Effective date", "skip": "Skip to content"},
    "ja": {"privacy": "プライバシー", "terms": "利用規約", "privacy_link": "プライバシーポリシー", "language": "言語", "toc": "目次", "top": "ページ上部へ", "updated": "施行日", "skip": "本文へ移動"},
    "zh": {"privacy": "隐私", "terms": "使用条款", "privacy_link": "隐私政策", "language": "语言", "toc": "目录", "top": "返回顶部", "updated": "生效日期", "skip": "跳到正文"},
    "es": {"privacy": "Privacidad", "terms": "Términos", "privacy_link": "Política de privacidad", "language": "Idioma", "toc": "Contenido", "top": "Volver arriba", "updated": "Fecha de vigencia", "skip": "Saltar al contenido"},
    "pt": {"privacy": "Privacidade", "terms": "Termos", "privacy_link": "Política de Privacidade", "language": "Idioma", "toc": "Conteúdo", "top": "Voltar ao topo", "updated": "Data de vigência", "skip": "Ir para o conteúdo"},
}
TERMS_LINK = {"ko": "이용약관", "en": "Terms of Use", "ja": "利用規約", "zh": "使用条款", "es": "Términos de uso", "pt": "Termos de Uso"}

BASE_URL = "https://fellow-survivor-studio.github.io/reel-nest/"
URL_RE = re.compile(r"^https://[^\s]+$")
# Privacy policy: numbered sections ("1. ...") with lettered subsections ("A." / "가.")
PRIVACY_SECTION_RE = re.compile(r"^(\d+)\.\s+(.+)$")
PRIVACY_SUBSECTION_RE = re.compile(r"^(?:[AB]|[가나다라마바사아자차카타파하])\.\s*(.+)$")
# Terms of use: article headings in every language ("제5조의2 (…)", "Article 5-2 (…)", "第5条の2（…）", …)
TERMS_SECTION_RE = re.compile(
    r"^(?:제\d+조(?:의\d+)?\s*\(.+\)|Article \d+(?:-\d+)? \(.+\)|第\d+条(?:[の之]\d+)?[（(].+[)）]"
    r"|Artículo \d+(?:-\d+)? \(.+\)|Artigo \d+(?:-\d+)? \(.+\)|부칙|Addendum|附則|附则|Disposición adicional|Disposição final"
    r"|사업자 정보|Business Information|事業者情報|经营者信息|Información de la empresa|Informações da empresa)$"
)
BULLETS = ("- ", "・")


def output_path(doc: str, lang: str) -> str:
    """Path of a page relative to the site root, e.g. '', 'en/', 'terms/', 'terms/ja/'."""
    prefix = DOCUMENTS[doc]["prefix"]
    return prefix if lang == "ko" else f"{prefix}{lang}/"


def relative_href(from_path: str, to_path: str) -> str:
    depth = from_path.count("/")
    return "../" * depth + to_path


def render_document(doc: str, text: str) -> tuple[str, str, list[tuple[str, str]], list[str]]:
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
        is_section = (TERMS_SECTION_RE if doc == "terms" else PRIVACY_SECTION_RE).match(line)
        if is_section:
            close_list()
            section_id = f"section-{len(toc) + 1}"
            toc.append((section_id, line))
            body.append(f'<h2 id="{section_id}">{html.escape(line)}</h2>')
            continue
        if doc == "privacy" and PRIVACY_SUBSECTION_RE.match(line):
            close_list()
            body.append(f"<h3>{html.escape(line)}</h3>")
            continue
        bullet = next((b for b in BULLETS if line.startswith(b)), None)
        if bullet:
            if not in_list:
                body.append("<ul>")
                in_list = True
            body.append(f"<li>{html.escape(line[len(bullet):].strip())}</li>")
            continue
        close_list()
        if URL_RE.match(line):
            safe_url = html.escape(line, quote=True)
            body.append(f'<p class="external-link"><a href="{safe_url}" rel="noopener noreferrer">{safe_url}</a></p>')
        else:
            body.append(f"<p>{html.escape(line)}</p>")
    close_list()
    return title, effective, toc, body


def render_page(doc: str, lang: str, text: str) -> str:
    meta = LANGUAGES[lang]
    labels = LABELS[lang]
    here = output_path(doc, lang)
    title, effective, toc, body = render_document(doc, text)
    css_href = relative_href(here, "styles.css")
    canonical = BASE_URL + here
    language_items = []
    for code, item in LANGUAGES.items():
        current = ' aria-current="page"' if code == lang else ""
        language_items.append(
            f'<a href="{relative_href(here, output_path(doc, code))}" lang="{item["html_lang"]}"{current}>'
            f'{html.escape(item["name"])}</a>'
        )
    language_links = "".join(language_items)
    alternate_links = "\n".join(
        f'<link rel="alternate" hreflang="{item["html_lang"]}" href="{BASE_URL + output_path(doc, code)}">'
        for code, item in LANGUAGES.items()
    )
    toc_links = "".join(f'<li><a href="#{anchor}">{html.escape(label)}</a></li>' for anchor, label in toc)
    effective_value = re.sub(r"^[^:：]+[:：]\s*", "", effective)
    privacy_href = relative_href(here, output_path("privacy", lang))
    terms_href = relative_href(here, output_path("terms", lang))
    return f'''<!doctype html>
<html lang="{meta["html_lang"]}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{html.escape(DESCRIPTIONS[doc][lang], quote=True)}">
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
    <a class="brand" href="{relative_href(here, output_path(doc, "ko"))}" aria-label="Reel Nest">
      <span class="brand-mark" aria-hidden="true">R</span>
      <span><strong>Reel Nest</strong><small>{html.escape(labels[doc])}</small></span>
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
        <p class="eyebrow">Reel Nest · {html.escape(labels[doc])}</p>
        <h1>{html.escape(title)}</h1>
        <p class="effective"><span>{html.escape(labels["updated"])}</span>{html.escape(effective_value)}</p>
      </div>
      <div class="document-body">{''.join(body)}</div>
      <a class="back-to-top" href="#">↑ {html.escape(labels["top"])}</a>
    </article>
  </main>
  <footer><a href="{terms_href}">{html.escape(TERMS_LINK[lang])}</a> · <a href="{privacy_href}">{html.escape(labels["privacy_link"])}</a><br>© 2026 Fellow Survivor Studio · Reel Nest</footer>
</body>
</html>
'''


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copy2(ROOT / "styles.css", DIST / "styles.css")
    pages: list[str] = []
    for doc, info in DOCUMENTS.items():
        for lang in LANGUAGES:
            source = CONTENT / f"{info['source']}_{lang}.txt"
            if not source.exists():
                raise FileNotFoundError(source)
            path = output_path(doc, lang)
            output_dir = DIST / path
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "index.html").write_text(render_page(doc, lang, source.read_text(encoding="utf-8")), encoding="utf-8")
            pages.append(path)
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}sitemap.xml\n", encoding="utf-8")
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{BASE_URL}{path}</loc></url>\n" for path in pages) + "</urlset>\n"
    (DIST / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    # GitHub Pages is configured to publish from main/(root). Keep the generated
    # root files in sync while retaining dist/ as a self-contained build artifact.
    for name in (".nojekyll", "robots.txt", "sitemap.xml"):
        shutil.copy2(DIST / name, ROOT / name)
    for path in pages:
        target_dir = ROOT / path
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(DIST / path / "index.html", target_dir / "index.html")


if __name__ == "__main__":
    main()
