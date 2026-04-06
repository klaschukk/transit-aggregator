# Domain Switch: transit-serbia.com

## Steps

1. **Buy domain** transit-serbia.com

2. **DNS** — add A record:
   ```
   transit-serbia.com     A  81.28.248.71
   www.transit-serbia.com A  81.28.248.71
   ```

3. **Set BASE_URL** in systemd:
   ```bash
   sudo systemctl edit transit
   # Add under [Service]:
   # Environment="BASE_URL=https://transit-serbia.com"
   ```

4. **SSL certificate** via certbot:
   ```bash
   sudo certbot --nginx -d transit-serbia.com -d www.transit-serbia.com
   ```

5. **Restart**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart transit
   sudo nginx -s reload
   ```

6. **Verify** — all should show `https://transit-serbia.com`:
   ```bash
   curl -s https://transit-serbia.com/ | grep canonical
   curl -s https://transit-serbia.com/sitemap.xml | head -5
   curl -s https://transit-serbia.com/robots.txt
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
