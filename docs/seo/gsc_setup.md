# Search Engine Setup — Prevozni

## Google Search Console

### Setup
1. Go to https://search.google.com/search-console/
2. Add property → URL prefix → `https://prevozni.com`
3. Verification: DNS TXT record (via Cloudflare)
   ```
   TXT  prevozni.com  "google-site-verification=XXXXX"
   ```
4. Submit sitemap: `https://prevozni.com/sitemap.xml`
5. Request indexing for `/` (homepage)

### Post-Setup
- Coverage report: check weekly, fix errors within 48h
- Core Web Vitals: check monthly
- Sitemaps: verify all URLs indexed
- Mobile Usability: should be 0 issues

## Bing Webmaster Tools

### Setup
1. Go to https://www.bing.com/webmasters/
2. Option A: Import from Google Search Console (easiest)
3. Option B: Add manually → verify via DNS CNAME
   ```
   CNAME  _bing.prevozni.com  verify.bing.com
   ```
4. Submit sitemap: `https://prevozni.com/sitemap.xml`

### Post-Setup
- SEO reports: check monthly
- URL submission: submit key pages manually

## Yandex Webmaster (optional)

1. Go to https://webmaster.yandex.com/
2. Add site → verify via DNS TXT or meta tag
3. Submit sitemap

## Monitoring Checklist

| Task | Frequency | Tool |
|------|-----------|------|
| Coverage errors | Weekly | GSC |
| Core Web Vitals | Monthly | GSC / PageSpeed Insights |
| Sitemap status | After each data refresh | GSC |
| Search performance | Weekly | GSC (Performance tab) |
| Mobile usability | Monthly | GSC |
| Structured data errors | Weekly | GSC (Enhancements) |

## Structured Data Types

| Page Type | Schema | Status |
|-----------|--------|--------|
| Homepage `/` | WebSite + SearchAction | Verified |
| Route detail `/rute/{slug}/` | ItemList + BusTrip | Verified |
| City pair `/voznja/` | FAQPage + TravelAction | Verified |
| City hub `/gradski/{city}/` | CollectionPage | Verified |
| Line detail `/linija/{slug}/` | ItemList + BusStop | Verified |
| Stop detail `/stajaliste/{slug}/` | BusStop + GeoCoordinates | Verified |
| Carriers `/prevoznici/` | ItemList + Organization | Verified |
| About `/o-nama/` | Organization | Verified |
| Contact `/kontakt/` | ContactPage | Verified |
| All inner pages | BreadcrumbList | Verified |
