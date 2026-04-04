#!/usr/bin/env python3
"""Comprehensive QA check for Transit Serbia production site."""

import json
import re
import subprocess
import sys

BASE = "http://81.28.248.71:5000"

URLS = [
    ("/", 200),
    ("/rute/", 200),
    ("/rute/beograd-novi-sad/", 200),
    ("/rute/beograd-nis/", 200),
    ("/voznja/beograd-do-novi-sad/", 200),
    ("/pretraga/", 200),
    ("/pretraga/?od=Beograd&do=Novi+Sad", 200),
    ("/gradski/beograd/", 200),
    ("/gradski/beograd/linija/linija-2a/", 200),
    ("/gradski/beograd/stajaliste/sajam/", 200),
    ("/prevoznici/", 200),
    ("/autobuske-stanice/", 200),
    ("/o-nama/", 200),
    ("/kontakt/", 200),
    ("/health", 200),
    ("/sitemap.xml", 200),
    ("/robots.txt", 200),
    ("/api/cities?q=beo", 200),
    ("/api/city-stops?sw_lat=44.7&sw_lon=20.3&ne_lat=44.9&ne_lon=20.6", 200),
    ("/api/stop-arrivals?slug=sajam", 200),
    ("/NEPOSTOJECI", 404),
]

EMOJI_PATTERN = re.compile(
    "[\U0001F4CD\U0001F50D\U0001F68C\U0001F682\U000023F0\U0001F4B0\U0001F4CF"
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F900-\U0001F9FF"
    "\U00002702-\U000027B0"
    "\U0000FE00-\U0000FE0F"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "\U00002600-\U000026FF"
    "\U0000200D"
    "\U00002764]"
)


def curl_page(url):
    """Fetch page via curl, return (status_code, body)."""
    full = BASE + url
    try:
        r = subprocess.run(
            ["curl", "-s", "-o", "-", "-w", "\n__STATUS__%{http_code}", "-L",
             "--max-time", "15", full],
            capture_output=True, text=True, timeout=20
        )
        output = r.stdout
        parts = output.rsplit("\n__STATUS__", 1)
        if len(parts) == 2:
            body = parts[0]
            status = int(parts[1].strip())
        else:
            body = output
            status = 0
        return status, body
    except Exception as e:
        return 0, f"CURL ERROR: {e}"


def check_page(url, expected_status):
    """Run all checks, return list of issues."""
    issues = []
    status, body = curl_page(url)

    # Determine page type
    is_html = "<html" in body.lower() or "<!" in body[:100]
    is_xml = url.endswith(".xml")
    is_json = url.startswith("/api/") or url == "/health"
    is_text = url == "/robots.txt"

    # 1. Status code
    if status != expected_status:
        issues.append(f"Status {status} (expected {expected_status})")
        if status == 0:
            return issues  # can't check further

    # 2. Traceback / Internal Server Error
    if "Traceback" in body:
        issues.append("Contains 'Traceback' (Python error)")
    if "Internal Server Error" in body and status != 500:
        issues.append("Contains 'Internal Server Error'")

    # For non-HTML pages, limited checks
    if is_json:
        try:
            data = json.loads(body)
        except json.JSONDecodeError as e:
            issues.append(f"Invalid JSON: {e}")
        return issues

    if is_xml:
        if "<urlset" not in body and "<sitemapindex" not in body:
            issues.append("XML sitemap missing <urlset> or <sitemapindex>")
        if "localhost" in body:
            issues.append("Sitemap contains 'localhost'")
        return issues

    if is_text:
        if "Sitemap:" not in body and "User-agent" not in body:
            issues.append("robots.txt missing expected directives")
        return issues

    if not is_html:
        return issues

    # --- HTML checks ---

    # 3. <title> exists and not "None"
    title_match = re.search(r"<title[^>]*>(.*?)</title>", body, re.DOTALL | re.IGNORECASE)
    if not title_match:
        issues.append("Missing <title>")
    else:
        title_text = title_match.group(1).strip()
        if not title_text:
            issues.append("<title> is empty")
        if "None" in title_text:
            issues.append(f"<title> contains 'None': {title_text[:80]}")

    # 4. <meta name="description"> exists
    if not re.search(r'<meta\s+name=["\']description["\']', body, re.IGNORECASE):
        # Also check reverse attribute order
        if not re.search(r'<meta\s+content=["\'][^"\']*["\']\s+name=["\']description["\']', body, re.IGNORECASE):
            if expected_status == 200:  # don't require on 404
                issues.append("Missing <meta name=\"description\">")

    # 5. rel="canonical" exists and no localhost
    canonical_match = re.search(r'rel=["\']canonical["\'][^>]*href=["\']([^"\']*)["\']', body, re.IGNORECASE)
    if not canonical_match:
        # Try reverse order
        canonical_match = re.search(r'href=["\']([^"\']*)["\'][^>]*rel=["\']canonical["\']', body, re.IGNORECASE)
    if not canonical_match:
        if expected_status == 200:
            issues.append("Missing rel=\"canonical\"")
    else:
        canonical_url = canonical_match.group(1)
        if "localhost" in canonical_url:
            issues.append(f"Canonical contains 'localhost': {canonical_url}")
        if "None" in canonical_url:
            issues.append(f"Canonical contains 'None': {canonical_url}")

    # 6. Literal "None" in main content
    main_match = re.search(r"<main[^>]*>(.*?)</main>", body, re.DOTALL | re.IGNORECASE)
    if main_match:
        main_content = main_match.group(1)
        # Strip HTML tags for text-level check
        text_only = re.sub(r"<[^>]+>", " ", main_content)
        # Find standalone "None" (not part of another word)
        none_matches = re.findall(r"\bNone\b", text_only)
        if none_matches:
            # Get context around first match
            idx = text_only.find("None")
            ctx = text_only[max(0, idx - 30):idx + 34].strip()
            ctx = re.sub(r"\s+", " ", ctx)
            issues.append(f"Literal 'None' in <main> ({len(none_matches)}x): ...{ctx}...")

    # 7. Emoji characters
    emojis_found = EMOJI_PATTERN.findall(body)
    if emojis_found:
        unique = set(emojis_found)
        issues.append(f"Emoji found: {' '.join(unique)} ({len(emojis_found)}x)")

    # 8. Inline style= attributes (excluding style="background:)
    style_matches = re.findall(r'style="([^"]*)"', body)
    non_bg_styles = [s for s in style_matches if not s.strip().startswith("background")]
    if len(non_bg_styles) > 5:
        # Sample some
        samples = non_bg_styles[:3]
        issues.append(f"Inline style= attributes (non-background): {len(non_bg_styles)} (e.g. {samples[0][:50]})")

    # 9. JSON-LD exists and is parseable
    ld_matches = re.findall(
        r'<script\s+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        body, re.DOTALL | re.IGNORECASE
    )
    if not ld_matches and expected_status == 200 and url not in ("/health", "/pretraga/"):
        issues.append("Missing JSON-LD (application/ld+json)")
    for i, ld in enumerate(ld_matches):
        try:
            json.loads(ld)
        except json.JSONDecodeError as e:
            issues.append(f"JSON-LD #{i+1} parse error: {e}")

    return issues


def main():
    print(f"QA Check: {BASE}")
    print(f"Checking {len(URLS)} URLs...\n")

    results = []
    for url, expected in URLS:
        issues = check_page(url, expected)
        results.append((url, expected, issues))

    # Print table
    max_url = max(len(r[0]) for r in results)
    hdr_url = "URL".ljust(max_url)
    print(f"| {hdr_url} | Status | Result")
    print(f"|{'-' * (max_url + 2)}|--------|" + "-" * 70)

    total_issues = 0
    for url, expected, issues in results:
        status_str = f"{expected}".ljust(6)
        if issues:
            total_issues += len(issues)
            issue_str = "; ".join(issues)
            print(f"| {url.ljust(max_url)} | {status_str} | ISSUES: {issue_str}")
        else:
            print(f"| {url.ljust(max_url)} | {status_str} | OK")

    print(f"\n{'=' * 80}")
    print(f"Total: {len(URLS)} URLs checked, {total_issues} issues found across {sum(1 for _, _, i in results if i)} pages")

    # Summary of issues only
    if total_issues:
        print(f"\n--- ISSUE SUMMARY ---")
        for url, expected, issues in results:
            if issues:
                for iss in issues:
                    print(f"  [{url}] {iss}")

    return 1 if total_issues else 0


if __name__ == "__main__":
    sys.exit(main())
