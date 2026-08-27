# Деплой — гайд

> **Обновлено 2026-08-27.** Прод-чекаут = дев-чекаут =
> `/home/deploy/transit-aggregator`, юзер `deploy`. Предыдущая версия
> этого файла (описывала старый сервер, лежавший ~месяц из-за
> просроченной оплаты у хостера) — в
> `docs/90_archive/06_tech/deploy_guide-2026-06-12-old-server.md`.

## Единственный подтверждённо рабочий способ — вручную на боксе

```bash
cd /home/deploy/transit-aggregator
./scripts/deploy.sh          # деплоит main
./scripts/deploy.sh <branch> # или конкретную ветку
```

Делает: `git fetch` + `git reset --hard origin/<branch>` → `pip install
-r requirements.txt` → `scripts/minify_css.py` → `sudo systemctl restart
prevozni` → health-check по unix-сокету (`/run/prevozni/prevozni.sock`).
Падает с ненулевым кодом, если `/health` не вернул 200 после рестарта.

`git reset --hard` стирает незакоммиченное в чекауте — коммить перед
тем, как надолго уходить от бокса.

## ⚠️ GitLab CI кнопка ▶ — СЕЙЧАС НЕ РАБОТАЕТ

`.gitlab-ci.yml` → job `deploy` всё ещё нацелен на старый, мёртвый
сервер:

```yaml
variables:
  DEPLOY_HOST: "178.105.76.3"     # старый сервер, недоступен
  DEPLOY_USER: "root"             # текущий деплой-юзер — deploy, не root
  DEPLOY_DIR: "/opt/prevozni"     # текущий чекаут — /home/deploy/transit-aggregator
# script делает systemctl restart transit (сервис теперь prevozni)
# и health-check по http://127.0.0.1:8000/health (теперь unix-сокет, не TCP :8000)
```

Даже если поправить хост/юзер/директорию/имя сервиса, **аутентификация
всё равно не пройдёт**: CI/CD-переменная `DEPLOY_SSH_KEY` — это ключ под
старую пару `root@178.105.76.3`. На текущем боксе в
`/home/deploy/.ssh/authorized_keys` лежит только один ключ —
`klaschuk@macbook.local` (личный ключ юзера, добавлен при переезде
2026-07-31) — это не CI-ключ, и класть личный ключ в CI-секрет не
стоит.

**Чтобы починить кнопку по-настоящему, нужно:**

1. Сгенерировать отдельную ED25519-пару только для CI-деплоя.
2. Публичный ключ — в `/home/deploy/.ssh/authorized_keys` на боксе.
3. Приватный ключ (base64) — в GitLab → Settings → CI/CD → Variables →
   `DEPLOY_SSH_KEY` (заменить текущее значение).
4. В `.gitlab-ci.yml` поправить `DEPLOY_HOST`/`DEPLOY_USER`/`DEPLOY_DIR`
   на текущие значения и заменить inline-скрипт на просто
   `ssh deploy@<host> 'cd /home/deploy/transit-aggregator && ./scripts/deploy.sh'`
   — не дублировать шаги deploy.sh второй раз внутри CI.

Это провижининг новых SSH-доступов к продовому боксу — не делаю это
молча без подтверждения. До починки: деплой **только вручную**, шагом
выше.

## Troubleshooting

- `/health` не 200 после деплоя → смотри `journalctl -u prevozni -n 50`
  и `logs/error.log` в чекауте.
- CSS не обновился → `scripts/minify_css.py` пишет в
  `static/css/dist/` (gitignored) — если деплоил не через `deploy.sh`,
  этот шаг мог быть пропущен.
- Ночной пайплайн держит write-lock DuckDB → см. корневой `CLAUDE.md` →
  «Окно обслуживания» (`logs/.maintenance` флаг).
