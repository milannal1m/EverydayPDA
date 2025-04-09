
# EverydayPDA

## Table of Contents

1. [Coverage](#coverage)
2. [API](#api)
3. [Docker](#docker)
4. [GIT](#git)

## Coverage

![Coverage](https://img.shields.io/badge/Coverage-75.1%25-brightgreen)

| Datei | Coverage (%) |
|---|---|
| backend/UseCases.py | 95.5% |
| backend/api/AnswerProcessor.py | 76.8% |
| backend/api/database.py | 75.0% |
| backend/api/main.py | 81.8% |
| backend/api/models.py | 100.0% |
| backend/api/preference_endpoints.py | 100.0% |
| backend/llm_fetchers/ChatGPTProcessor.py | 90.0% |
| backend/llm_fetchers/UseCaseProcessor.py | 78.6% |
| backend/service_fetchers/services.py | 46.0% |
| frontend/api_client.py | 62.9% |
| **Projekt** | **75.1%** |

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