
# EverydayPDA

## Table of Contents

1. [Coverage](#coverage)
2. [API](#api)
3. [Docker](#docker)
4. [GIT](#git)

## Coverage

![Coverage](https://img.shields.io/badge/Coverage-55.7%25-brightgreen)

| Datei | Coverage (%) |
|---|---|
| backend/UseCases.py | 100.0% |
| backend/api/AnswerProcessor.py | 33.3% |
| backend/api/database.py | 75.0% |
| backend/api/main.py | 84.4% |
| backend/api/models.py | 100.0% |
| backend/api/preference_endpoints.py | 100.0% |
| backend/llm_fetchers/ChatGPTProcessor.py | 96.2% |
| backend/llm_fetchers/UseCaseProcessor.py | 38.2% |
| backend/service_fetchers/services.py | 36.8% |
| frontend/api_handler.py | 79.2% |
| frontend/bot.py | 27.6% |
| frontend/tts_stt.py | 23.5% |
| **Projekt** | **55.7%** |

## API

The REST API is running on [Localhost](http://localhost:8000) with a complete [documentation](http://localhost:8000/docs).

However, you need to start [Docker](#docker) for this.

## Docker

Start Docker:
```bash
docker compose up -d --build
```

## Git

How to clone:
```bash
git clone https://github.com/milannal1m/EverydayPDA.git
```

How to push
```bash
git add .
git commit -m "Message"
git push origin <branch>
```

How to pull
```bash
git pull --rebase origin main
```

Mergen
```bash
git checkout main
git merge <branch-name>
```

Branch erstellen
```bash
git branch <branch-name>
```

In Branch wechseln
```bash
git checkout -b <branch-name>
```

Branch löschen (lokal und remote)
```bash
git branch -D <branch-name>
git push origin --delete <branch-name>
```