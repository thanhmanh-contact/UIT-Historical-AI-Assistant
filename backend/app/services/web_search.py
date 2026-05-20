"""
web_search.py — Web RAG Fallback Service (v2.3 — đã sửa lỗi parser)

FIXES v2.3:
  - Sửa DuckDuckGo parser: selector `a.result__url` không tồn tại → dùng `a.result__a`
  - Thêm Google scrape fallback khi DuckDuckGo thất bại
  - Thêm direct page heuristic theo từ khoá (hiệu trưởng, tuyển sinh, học phí, v.v.)
  - Tăng số trang tải tối thiểu lên 3
"""

import re
import time
import requests
from urllib.parse import quote_plus, unquote, parse_qs, urlparse
from app.config import settings
from app.utils.logger import app_logger

TRUSTED_UIT_DOMAINS = [
    "uit.edu.vn",
    "tuyensinh.uit.edu.vn",
    "daa.uit.edu.vn",
    "sv.uit.edu.vn",
    "cnpm.uit.edu.vn",
    "se.uit.edu.vn",
]

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Heuristic: từ khoá → URL UIT trực tiếp (dùng khi search engine thất bại)
_DIRECT_PAGES = [
    (
        ["hiệu trưởng", "ban lãnh đạo", "ban giám hiệu", "lãnh đạo trường",
         "hiệu phó", "rector", "principal", "hiệu"],
        "https://www.uit.edu.vn/gioi-thieu/ban-lanh-dao",
    ),
    (
        ["lịch sử", "thành lập", "giới thiệu", "tổng quan", "history",
         "overview", "20 năm", "kỷ niệm", "hình thành", "thành tựu", "thành tích", "đạt được"],
        "https://www.uit.edu.vn/gioi-thieu",
    ),
    (
        ["tuyển sinh", "xét tuyển", "điểm chuẩn", "chỉ tiêu", "đăng ký",
         "hồ sơ", "thí sinh", "admission", "nhập học"],
        "https://tuyensinh.uit.edu.vn/",
    ),
    (
        ["học phí", "chi phí học", "học bổng", "miễn giảm", "tuition", "fee"],
        "https://daa.uit.edu.vn/hoc-phi",
    ),
    (
        ["chương trình đào tạo", "ngành học", "chuyên ngành", "curriculum"],
        "https://daa.uit.edu.vn/chuong-trinh-dao-tao",
    ),
    (
        ["sinh viên", "student", "câu lạc bộ", "hoạt động ngoại khóa",
         "ký túc xá", "dorm"],
        "https://sv.uit.edu.vn/",
    ),
    (
        ["cơ sở vật chất", "campus", "địa chỉ", "thư viện", "library",
         "phòng lab", "facility"],
        "https://www.uit.edu.vn/gioi-thieu/co-so-vat-chat",
    ),
    (
        ["nghiên cứu", "research", "giải thưởng", "award", "công trình khoa học", "huân chương", "huy chương"],
        "https://www.uit.edu.vn/nghien-cuu",
    ),
    (
        ["cnpm", "công nghệ phần mềm", "khoa phần mềm", "software engineering",
         "selab", "se "],
         "https://se.uit.edu.vn/gioi-thieu",
    ),
    (
        ["liên kết quốc tế", "hợp tác quốc tế", "international", "đối tác"],
        "https://www.uit.edu.vn/hop-tac-quoc-te",
    ),
]


def _is_trusted_url(url: str) -> bool:
    return any(domain in url for domain in TRUSTED_UIT_DOMAINS)


def _clean_html_text(html_text: str) -> str:
    text = re.sub(r'\n{3,}', '\n\n', html_text)
    text = re.sub(r'[ \t]+', ' ', text)
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    return '\n'.join(lines)


def _fetch_page_text(url: str, max_chars: int = 2500) -> tuple:
    """Tải trang web, trả về (title, cleaned_text). Trả về ('', '') nếu thất bại."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        app_logger.error("❌ BeautifulSoup4 chưa được cài: pip install beautifulsoup4")
        return "", ""

    try:
        resp = requests.get(
            url, headers=_HEADERS,
            timeout=settings.WEB_SEARCH_TIMEOUT,
            allow_redirects=True,
        )
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else url

        for tag in soup(["script", "style", "nav", "footer", "header",
                         "noscript", "aside", "iframe", "form"]):
            tag.decompose()

        main_content = (
            soup.find("main") or
            soup.find("article") or
            soup.find(id=re.compile(r"content|main|body", re.I)) or
            soup.find(class_=re.compile(r"content|main|entry|post", re.I)) or
            soup.body
        )

        raw_text = main_content.get_text(separator="\n") if main_content else soup.get_text(separator="\n")
        clean_text = _clean_html_text(raw_text)
        return title, clean_text[:max_chars]

    except requests.Timeout:
        app_logger.warning(f"⏱️  Timeout khi tải {url}")
        return "", ""
    except requests.RequestException as e:
        app_logger.warning(f"⚠️  Lỗi HTTP {url}: {e}")
        return "", ""
    except Exception as e:
        app_logger.error(f"❌ Lỗi khi xử lý {url}: {e}", exc_info=True)
        return "", ""


def _extract_ddg_url(href: str) -> str:
    """Giải mã URL redirect DuckDuckGo (/l/?uddg=...)."""
    if not href:
        return ""
    if "uddg=" in href:
        parsed = parse_qs(urlparse(href).query)
        uddg = parsed.get("uddg", [""])[0]
        return unquote(uddg) if uddg else ""
    if href.startswith("http"):
        return href
    return ""


def _search_duckduckgo(query: str, site_restrict: str = "uit.edu.vn") -> list:
    """
    Tìm kiếm DuckDuckGo HTML.
    FIX v2.3: Chỉ dùng `a.result__a` (đây là thẻ <a> thực sự có href).
    `a.result__url` KHÔNG đúng — đó là <span>, không phải <a>.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return []

    search_query = f"site:{site_restrict} {query}"
    ddg_url = f"https://html.duckduckgo.com/html/?q={quote_plus(search_query)}&kl=vn-vi"

    try:
        resp = requests.get(ddg_url, headers=_HEADERS, timeout=settings.WEB_SEARCH_TIMEOUT)
        soup = BeautifulSoup(resp.text, "html.parser")

        urls = []
        for a in soup.select("a.result__a"):  # FIX: loại bỏ `a.result__url` sai
            href = a.get("href", "")
            real_url = _extract_ddg_url(href)
            if real_url and _is_trusted_url(real_url) and real_url not in urls:
                urls.append(real_url)

        app_logger.info(f"🔎 DuckDuckGo: {len(urls)} URL từ site:{site_restrict}")
        return urls[:settings.WEB_SEARCH_MAX_RESULTS + 3]

    except Exception as e:
        app_logger.warning(f"⚠️  DuckDuckGo lỗi: {e}")
        return []


def _search_google_scrape(query: str, site_restrict: str = "uit.edu.vn") -> list:
    """
    Fallback: Scrape Google (không API key) khi DuckDuckGo thất bại.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return []

    search_query = f"site:{site_restrict} {query}"
    google_url = f"https://www.google.com/search?q={quote_plus(search_query)}&hl=vi&num=5"

    try:
        resp = requests.get(google_url, headers=_HEADERS, timeout=settings.WEB_SEARCH_TIMEOUT)
        soup = BeautifulSoup(resp.text, "html.parser")

        urls = []
        for a in soup.select("a[href]"):
            href = a.get("href", "")
            if href.startswith("/url?"):
                parsed = parse_qs(urlparse(href).query)
                real = parsed.get("q", [""])[0]
            elif href.startswith("http"):
                real = href
            else:
                continue

            if real and _is_trusted_url(real) and real not in urls:
                urls.append(real)

        app_logger.info(f"🔎 Google scrape: {len(urls)} URL từ site:{site_restrict}")
        return urls[:settings.WEB_SEARCH_MAX_RESULTS + 3]

    except Exception as e:
        app_logger.warning(f"⚠️  Google scrape lỗi: {e}")
        return []


def _get_direct_pages(query: str) -> list:
    """Dựa trên từ khoá trong câu hỏi → trả về URL UIT trực tiếp (không qua search engine)."""
    query_lower = query.lower()
    matched = []
    for keywords, url in _DIRECT_PAGES:
        if any(kw in query_lower for kw in keywords):
            if url not in matched:
                matched.append(url)
    return matched


def search_uit_web(query: str, scope: str = "uit") -> tuple:
    """
    Tìm kiếm thông tin trên web UIT theo câu hỏi (v2.3).

    Chiến lược:
      1. DuckDuckGo (đã fix parser)
      2. Google scrape fallback
      3. Direct page heuristic từ khoá
      → Tổng hợp context + sources

    Returns:
        (context_text, sources_list)
    """
    if not settings.WEB_SEARCH_ENABLED:
        return "", []

    app_logger.info(f"🌐 Web RAG | scope={scope} | query={query[:60]}")

    site_restrict = "se.uit.edu.vn" if scope == "cnpm" else "uit.edu.vn"

    # 1. DuckDuckGo
    candidate_urls = _search_duckduckgo(query, site_restrict=site_restrict)
    if not candidate_urls and scope == "cnpm":
        candidate_urls = _search_duckduckgo(query, site_restrict="uit.edu.vn")

    # 2. Google Fallback
    if not candidate_urls:
        app_logger.info("🔄 DuckDuckGo trống → thử Google scrape")
        candidate_urls = _search_google_scrape(query, site_restrict=site_restrict)
        if not candidate_urls and scope == "cnpm":
            candidate_urls = _search_google_scrape(query, site_restrict="uit.edu.vn")

    # 3. Direct page heuristic
    for u in _get_direct_pages(query):
        if u not in candidate_urls:
            candidate_urls.append(u)

    if not candidate_urls:
        app_logger.warning("⚠️  Web RAG: Không tìm được URL nào.")
        return "", []

    # 4. Tải nội dung
    context_parts = []
    sources = []
    max_fetch = max(settings.WEB_SEARCH_MAX_RESULTS, 3)

    for url in candidate_urls[:max_fetch]:
        title, text = _fetch_page_text(url)
        if text and len(text) > 100:
            context_parts.append(f"[Nguồn: {url}]\n{text}")
            sources.append({"url": url, "title": title, "source_type": "web"})
            app_logger.info(f"✅ Web RAG: {len(text)} ký tự từ {url}")
        else:
            app_logger.info(f"⚪ Web RAG: nội dung rỗng/ngắn từ {url}")
        time.sleep(0.3)

    if not context_parts:
        app_logger.warning("⚠️  Web RAG: Tất cả trang đều rỗng.")
        return "", []

    return "\n\n---\n\n".join(context_parts), sources
