# Domain Switch: prevozni.com

## Steps

1. **Buy domain** prevozni.com

2. **DNS** — add A record:
   ```
   prevozni.com     A  81.28.248.71
   www.prevozni.com A  81.28.248.71
   ```

3. **Set BASE_URL** in systemd:
   ```bash
   sudo systemctl edit transit
   # Add under [Service]:
   # Environment="BASE_URL=https://prevozni.com"
   ```

4. **SSL certificate** via certbot:
   ```bash
   sudo certbot --nginx -d prevozni.com -d www.prevozni.com
   ```

5. **Restart**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart transit
   sudo nginx -s reload
   ```

6. **Verify** — all should show `https://prevozni.com`:
   ```bash
   curl -s https://prevozni.com/ | grep canonical
   curl -s https://prevozni.com/sitemap.xml | head -5
   curl -s https://prevozni.com/robots.txt
   ```

## What changes automatically

- `canonical` URL on all pages (via `config.BASE_URL`)
- `og:url` meta tags
- `sitemap.xml` all URLs
- `robots.txt` Sitemap URL
- JSON-LD URLs in breadcrumbs

No code changes needed — everything reads from `config.BASE_URL`.

## Rollback

Set `BASE_URL=http://81.28.248.71` in systemd env and restart.
