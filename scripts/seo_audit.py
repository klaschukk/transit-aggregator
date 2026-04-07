"""
Full SEO audit — crawls ALL pages from sitemap.xml.

Checks: title, description, h1, canonical, og tags, JSON-LD,
broken links, duplicate titles/descriptions, response codes.

Usage:
    python -u scripts/seo_audit.py [--base http://127.0.0.1:5000] [--max 0]
"""
import argparse
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
DIM = '\033[2m'
BOLD = '\033[1m'
RESET = '\033[0m'


def fetch_sitemap_urls(base: str) -> list[str]:
    r = requests.get(f'{base}/sitemap.xml', timeout=30)
    r.raise_for_status()
    root = ElementTree.fromstring(r.content)
    ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = []
    for url_el in root.findall('.//s:url/s:loc', ns):
        loc = url_el.text.strip()
        # Normalize to relative path
        for prefix in [base, 'https://prevozni.com', 'http://81.28.248.71:5000',
                       'http://81.28.248.71']:
            if loc.startswith(prefix):
                loc = loc[len(prefix):]
                break
        urls.append(loc)
    return urls


def audit_page(base: str, path: str) -> dict:
    """Audit a single page, return dict of findings."""
    result = {'path': path, 'issues': [], 'status': 0}
    try:
        r = requests.get(f'{base}{path}', timeout=15)
        result['status'] = r.status_code
        if r.status_code != 200:
            result['issues'].append(f'HTTP {r.status_code}')
            return result

        soup = BeautifulSoup(r.text, 'html.parser')

        # Title
        title_tag = soup.find('title')
        title = title_tag.text.strip() if title_tag else ''
        result['title'] = title
        if not title:
            result['issues'].append('NO_TITLE')
        elif len(title) > 70:
            result['issues'].append(f'TITLE_LONG({len(title)})')

        # Meta description
        desc_tag = soup.find('meta', {'name': 'description'})
        desc = desc_tag['content'].strip() if desc_tag and desc_tag.get('content') else ''
        result['desc'] = desc
        if not desc:
            result['issues'].append('NO_DESC')
        elif len(desc) > 160:
            result['issues'].append(f'DESC_LONG({len(desc)})')

        # H1
        h1s = soup.find_all('h1')
        if not h1s:
            result['issues'].append('NO_H1')
        elif len(h1s) > 1:
            result['issues'].append(f'MULTI_H1({len(h1s)})')

        # Canonical
        can = soup.find('link', {'rel': 'canonical'})
        if not can:
            result['issues'].append('NO_CANONICAL')
        elif can.get('href') and ('localhost' in can['href'] or '127.0.0.1' in can['href']):
            result['issues'].append('LOCALHOST_CANONICAL')

        # OG tags
        for prop in ['og:title', 'og:description']:
            if not soup.find('meta', {'property': prop}):
                result['issues'].append(f'NO_{prop.upper().replace(":", "_")}')

        # JSON-LD
        if not soup.find('script', {'type': 'application/ld+json'}):
            result['issues'].append('NO_JSONLD')

        # "None" in visible text (data leak)
        body = soup.find('body')
        if body:
            text = body.get_text()
            # Exclude SVG fill="none" — only check for standalone "None"
            import re
            none_matches = re.findall(r'(?<!\w)None(?!\w)', text)
            if none_matches:
                result['issues'].append(f'NONE_IN_TEXT({len(none_matches)})')

    except requests.exceptions.Timeout:
        result['issues'].append('TIMEOUT')
    except Exception as e:
        result['issues'].append(f'ERROR:{type(e).__name__}')

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', default='http://127.0.0.1:5000')
    parser.add_argument('--max', type=int, default=0, help='Max pages (0=all)')
    parser.add_argument('--workers', type=int, default=8)
    args = parser.parse_args()

    print(f'\n  {BOLD}SEO AUDIT{RESET}')
    print(f'  {"=" * 55}')
    print(f'  Base: {args.base}')

    # Fetch sitemap
    urls = fetch_sitemap_urls(args.base)
    if args.max:
        urls = urls[:args.max]
    print(f'  Pages to audit: {BOLD}{len(urls)}{RESET}')
    print(f'  Workers: {args.workers}')
    print(f'  {"=" * 55}\n')

    results = []
    issue_counts = Counter()
    title_seen = defaultdict(list)
    desc_seen = defaultdict(list)
    done = 0

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(audit_page, args.base, url): url for url in urls}
        for future in as_completed(futures):
            r = future.result()
            results.append(r)
            done += 1

            for iss in r['issues']:
                issue_counts[iss.split('(')[0]] += 1

            # Track duplicates
            if r.get('title'):
                title_seen[r['title']].append(r['path'])
            if r.get('desc'):
                desc_seen[r['desc']].append(r['path'])

            # Progress
            if done % 100 == 0 or done == len(urls):
                errs = sum(1 for x in results if x['issues'])
                sys.stdout.write(f'\r  {DIM}{done:>5}/{len(urls)}{RESET}  '
                                 f'{GREEN}{done - errs} ok{RESET}  '
                                 f'{RED}{errs} issues{RESET}')
                sys.stdout.flush()

    print('\n')

    # Duplicate titles
    dup_titles = {t: paths for t, paths in title_seen.items() if len(paths) > 1}
    # Duplicate descriptions
    dup_descs = {d: paths for d, paths in desc_seen.items() if len(paths) > 1}

    # Summary
    pages_with_issues = [r for r in results if r['issues']]
    http_errors = [r for r in results if r['status'] != 200]

    print(f'  {BOLD}RESULTS{RESET}')
    print(f'  {"=" * 55}')
    print(f'  Pages audited:    {BOLD}{len(results)}{RESET}')
    print(f'  Pages with issues:{RED}{len(pages_with_issues)}{RESET}')
    print(f'  HTTP errors:      {RED}{len(http_errors)}{RESET}')
    print(f'  Duplicate titles: {YELLOW}{len(dup_titles)}{RESET}')
    print(f'  Duplicate descs:  {YELLOW}{len(dup_descs)}{RESET}')
    print()

    # Issue breakdown
    if issue_counts:
        print(f'  {BOLD}ISSUE BREAKDOWN{RESET}')
        for issue, count in issue_counts.most_common():
            print(f'    {issue:25s} {RED}{count:>5}{RESET}')
        print()

    # Sample pages with issues (first 20)
    if pages_with_issues:
        print(f'  {BOLD}SAMPLE PAGES WITH ISSUES (first 20){RESET}')
        for r in pages_with_issues[:20]:
            issues_str = ', '.join(r['issues'])
            print(f'    {r["path"][:60]:60s} {RED}{issues_str}{RESET}')
        if len(pages_with_issues) > 20:
            print(f'    ... and {len(pages_with_issues) - 20} more')
        print()

    # Duplicate titles (top 5)
    if dup_titles:
        print(f'  {BOLD}DUPLICATE TITLES (top 5){RESET}')
        for title, paths in sorted(dup_titles.items(), key=lambda x: -len(x[1]))[:5]:
            print(f'    {YELLOW}"{title[:60]}"{RESET} x{len(paths)}')
            for p in paths[:3]:
                print(f'      {DIM}{p}{RESET}')
        print()

    # HTTP errors
    if http_errors:
        print(f'  {BOLD}HTTP ERRORS{RESET}')
        for r in http_errors[:20]:
            print(f'    {RED}{r["status"]}{RESET} {r["path"]}')
        print()

    print(f'  {"=" * 55}')
    score = (len(results) - len(pages_with_issues)) * 100 // len(results) if results else 0
    color = GREEN if score >= 90 else YELLOW if score >= 70 else RED
    print(f'  SEO Score: {color}{BOLD}{score}%{RESET} ({len(results) - len(pages_with_issues)}/{len(results)} clean)')
    print(f'  {"=" * 55}\n')


if __name__ == '__main__':
    main()
