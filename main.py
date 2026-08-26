from __future__ import annotations

import ipaddress
import socket
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from flask import Flask, Response, jsonify, render_template, request, url_for

app = Flask(__name__)

TIMEOUT = 12
MAX_HTML_BYTES = 2_000_000
USER_AGENT = "SiteMedicAudit/1.0 (+website quality audit)"

GUIDES = {
    "website-seo-audit": {
        "title": "Website SEO Audit: Find Technical SEO Problems",
        "description": "Check titles, descriptions, canonical URLs, headings, indexing signals and page structure, then prioritize the SEO fixes that matter.",
        "items": ["Verify indexability and the canonical URL", "Improve titles, descriptions and heading structure", "Review internal links, images and structured data"],
    },
    "website-speed-test": {
        "title": "Website Speed Test and Performance Troubleshooting",
        "description": "Diagnose slow server response, heavy pages and common mobile performance problems with a clear repair plan.",
        "items": ["Measure server response and redirect time", "Reduce render-blocking assets and page weight", "Add caching, compression and CDN delivery"],
    },
    "website-security-check": {
        "title": "Website Security Check: HTTPS, Headers and Mixed Content",
        "description": "Review essential browser-facing security signals, HTTPS delivery, mixed content and missing defensive headers.",
        "items": ["Enforce HTTPS everywhere", "Remove mixed-content requests", "Configure CSP, content-type and referrer headers"],
    },
    "mobile-friendly-test": {
        "title": "Mobile-Friendly Website Test and Repair Guide",
        "description": "Find mobile viewport, accessibility and usability problems that can frustrate visitors on smaller screens.",
        "items": ["Set a responsive viewport", "Use readable content and accessible controls", "Test navigation and layout on real devices"],
    },
    "website-accessibility-check": {
        "title": "Website Accessibility Check: Images, Links and Structure",
        "description": "Identify common page-level accessibility problems such as missing image text, unnamed links and unclear headings.",
        "items": ["Add useful image alternative text", "Give every link an accessible name", "Use a logical heading hierarchy"],
    },
    "fix-website-errors": {
        "title": "How to Find and Fix Common Website Errors",
        "description": "A practical workflow for finding HTTP, SEO, speed, security, mobile and accessibility problems on a public website.",
        "items": ["Capture a reproducible diagnostic report", "Prioritize user-impacting and critical faults", "Implement, test and monitor each correction"],
    },
}


def normalize_url(value: str) -> str:
    value = (value or "").strip()
    if not value:
        raise ValueError("Please enter a website URL.")
    if "://" not in value:
        value = "https://" + value
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Enter a valid HTTP or HTTPS website URL.")
    if parsed.username or parsed.password or parsed.port not in {None, 80, 443}:
        raise ValueError("This URL format is not supported.")
    return parsed.geturl()


def ensure_public_host(url: str) -> None:
    host = urlparse(url).hostname
    try:
        addresses = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise ValueError("The domain could not be resolved.") from exc
    for result in addresses:
        ip = ipaddress.ip_address(result[4][0])
        if not ip.is_global:
            raise ValueError("Private or local network addresses cannot be scanned.")


def issue(category: str, severity: str, title: str, detail: str, fix: str) -> dict:
    return {"category": category, "severity": severity, "title": title, "detail": detail, "fix": fix}


def audit_url(raw_url: str) -> dict:
    target = normalize_url(raw_url)
    started = time.perf_counter()
    current_url = target
    response = None
    for _ in range(6):
        ensure_public_host(current_url)
        response = requests.get(
            current_url,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"},
            timeout=TIMEOUT,
            allow_redirects=False,
            stream=True,
        )
        if response.is_redirect or response.is_permanent_redirect:
            location = response.headers.get("location")
            if not location:
                break
            current_url = normalize_url(urljoin(current_url, location))
            response.close()
            continue
        break
    else:
        raise ValueError("The website redirected too many times.")
    if response is None:
        raise ValueError("The website could not be reached.")
    chunks, total = [], 0
    for chunk in response.iter_content(65536):
        total += len(chunk)
        if total > MAX_HTML_BYTES:
            break
        chunks.append(chunk)
    elapsed_ms = round((time.perf_counter() - started) * 1000)
    html = b"".join(chunks).decode(response.encoding or "utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")
    issues = []

    if response.status_code >= 400:
        issues.append(issue("Availability", "critical", f"HTTP {response.status_code} response", "The page did not return a successful status code.", "Repair routing, deployment, or server configuration so the page returns HTTP 200."))
    if urlparse(response.url).scheme != "https":
        issues.append(issue("Security", "critical", "HTTPS is not enforced", "The final page is delivered over an unencrypted connection.", "Install a valid TLS certificate and redirect every HTTP request to HTTPS."))
    if elapsed_ms > 2500:
        issues.append(issue("Performance", "critical", "Very slow initial response", f"The audit request completed in {elapsed_ms} ms.", "Profile the backend, enable caching/CDN, and reduce server processing time."))
    elif elapsed_ms > 1000:
        issues.append(issue("Performance", "warning", "Slow initial response", f"The audit request completed in {elapsed_ms} ms.", "Enable caching and optimize server/database work before HTML is returned."))

    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    description_tag = soup.find("meta", attrs={"name": lambda value: value and value.lower() == "description"})
    description = (description_tag.get("content") or "").strip() if description_tag else ""
    h1s = soup.find_all("h1")
    canonical = soup.find("link", rel=lambda value: value and "canonical" in value)
    viewport = soup.find("meta", attrs={"name": lambda value: value and value.lower() == "viewport"})

    if not title:
        issues.append(issue("SEO", "critical", "Missing page title", "Search engines and browser tabs have no descriptive title.", "Add one unique, descriptive <title> of roughly 30–60 characters."))
    elif len(title) < 20 or len(title) > 65:
        issues.append(issue("SEO", "warning", "Page title length needs work", f"The title contains {len(title)} characters.", "Rewrite the title to be descriptive and approximately 30–60 characters."))
    if not description:
        issues.append(issue("SEO", "warning", "Missing meta description", "Search results may generate an uncontrolled snippet.", "Add a unique, helpful meta description of approximately 120–160 characters."))
    if len(h1s) == 0:
        issues.append(issue("SEO", "warning", "Missing H1 heading", "The page has no primary heading.", "Add one clear H1 that describes the page topic."))
    elif len(h1s) > 1:
        issues.append(issue("SEO", "info", "Multiple H1 headings", f"The page contains {len(h1s)} H1 elements.", "Keep a clear heading hierarchy and one primary page topic."))
    if not canonical:
        issues.append(issue("SEO", "warning", "Missing canonical URL", "Search engines have no explicit preferred URL for this page.", "Add a self-referencing canonical link with the final absolute URL."))
    if not viewport:
        issues.append(issue("Mobile", "critical", "Missing mobile viewport", "The layout may render poorly on phones.", "Add <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">."))

    images = soup.find_all("img")
    missing_alt = sum(1 for image in images if image.get("alt") is None)
    if missing_alt:
        issues.append(issue("Accessibility", "warning", "Images missing alternative text", f"{missing_alt} of {len(images)} images have no alt attribute.", "Add concise alt text to meaningful images and empty alt text to decorative images."))

    insecure = 0
    if urlparse(response.url).scheme == "https":
        for tag, attr in (("script", "src"), ("img", "src"), ("link", "href")):
            insecure += sum(1 for element in soup.find_all(tag) if str(element.get(attr, "")).startswith("http://"))
    if insecure:
        issues.append(issue("Security", "critical", "Mixed-content resources", f"Found {insecure} resource URLs loaded over HTTP on an HTTPS page.", "Serve every script, stylesheet, and image over HTTPS."))

    headers = {key.lower(): value for key, value in response.headers.items()}
    missing_security = [name for name in ("content-security-policy", "x-content-type-options", "referrer-policy") if name not in headers]
    if missing_security:
        issues.append(issue("Security", "warning", "Recommended security headers missing", ", ".join(missing_security), "Configure these headers at the application, proxy, or CDN layer."))

    links = [urljoin(response.url, a.get("href")) for a in soup.find_all("a", href=True)]
    empty_links = sum(1 for a in soup.find_all("a", href=True) if not (a.get_text(" ", strip=True) or a.get("aria-label") or a.find("img", alt=True)))
    if empty_links:
        issues.append(issue("Accessibility", "warning", "Links without accessible names", f"Found {empty_links} links with no readable label.", "Give every link visible text or a meaningful aria-label."))

    weights = {"critical": 18, "warning": 8, "info": 3}
    score = max(0, 100 - sum(weights[item["severity"]] for item in issues))
    counts = {level: sum(1 for item in issues if item["severity"] == level) for level in ("critical", "warning", "info")}
    return {
        "status": "success", "requested_url": target, "final_url": response.url,
        "http_status": response.status_code, "response_ms": elapsed_ms, "page_bytes": total,
        "score": score, "counts": counts, "issues": issues, "checks_run": 12,
        "summary": {"title": title or "Not found", "description": description or "Not found", "images": len(images), "links": len(links)},
        "disclaimer": "This automated single-page audit is a diagnostic snapshot. Full remediation begins only after access and scope are confirmed."
    }


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/guides/<slug>")
def guide(slug: str):
    guide_data = GUIDES.get(slug)
    if not guide_data:
        return render_template("404.html"), 404
    return render_template("guide.html", slug=slug, guide=guide_data)


@app.get("/robots.txt")
def robots():
    body = f"User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: {url_for('sitemap', _external=True)}\n"
    return Response(body, mimetype="text/plain")


@app.get("/sitemap.xml")
def sitemap():
    urls = [url_for("index", _external=True)] + [url_for("guide", slug=slug, _external=True) for slug in GUIDES]
    nodes = "".join(f"<url><loc>{url}</loc><changefreq>monthly</changefreq><priority>{'1.0' if n == 0 else '0.7'}</priority></url>" for n, url in enumerate(urls))
    return Response(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{nodes}</urlset>', mimetype="application/xml")


@app.get("/llms.txt")
def llms():
    return Response("# SiteMedic\nSiteMedic provides transparent automated website audits and optional expert remediation. Reports cover page-level SEO, performance, security, mobile and accessibility checks.\n", mimetype="text/plain")


@app.post("/api/audit")
def audit_site():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(audit_url(data.get("url", "")))
    except ValueError as exc:
        return jsonify({"status": "error", "message": str(exc)}), 400
    except requests.RequestException as exc:
        return jsonify({"status": "error", "message": f"The website could not be reached: {exc.__class__.__name__}."}), 502
    except Exception:
        app.logger.exception("Audit failed")
        return jsonify({"status": "error", "message": "The audit could not be completed. Please try again."}), 500


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
