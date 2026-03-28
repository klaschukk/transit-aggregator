# Инфраструктура

## Серверы

| Нода | Роль |
|------|------|
| pumba | K8s control plane + worker |
| simba | K8s worker |
| timon | K8s worker |

Все ноды на сервере в Подгорице (montiko).

## Деплой pipeline

```
git tag v1.0.0
    ↓
GitLab CI (build Docker image)
    ↓
Push to GitLab Container Registry
    ↓
ArgoCD (watches tag, deploys to K8s)
    ↓
Cloudflare (CDN + SSL + WAF)
```

## K8s структура

```
namespace: transit
├── Deployment: transit-web (Flask + gunicorn)
├── CronJob: transit-data-refresh (ежедневно 04:00)
├── PersistentVolumeClaim: transit-duckdb
├── ConfigMap: transit-config
└── Service + Ingress
```

## База данных

DuckDB файл (`transit.duckdb`) хранится в PersistentVolume.
Flask читает в read-only режиме. CronJob пересобирает файл из скраперов.

## Cloudflare

- SSL: Flexible или Full
- Cache: агрессивное кеширование статики (CSS, JS)
- WAF: базовые правила
- Analytics: отключены (используем Umami)

## Umami (аналитика)

Self-hosted, GDPR-compliant, без cookie-баннера.
Отслеживаем: pageviews, популярные маршруты, bounce rate, источники трафика.

## Переменные окружения

```
SECRET_KEY=...
FLASK_ENV=production
DUCKDB_PATH=/data/transit.duckdb
```
