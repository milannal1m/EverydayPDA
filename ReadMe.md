
# EverydayPDA

## Table of Contents

1. [Coverage](#coverage)
2. [API](#api)
3. [Docker](#docker)
4. [GIT](#git)

## Coverage

![Coverage](https://img.shields.io/badge/Coverage-24.8%25-brightgreen)

| Datei | Coverage (%) |
|---|---|
| backend/UseCases.py | 9.1% |
| backend/api/AnswerProcessor.py | 6.7% |
| backend/api/main.py | 25.0% |
| backend/llm_fetchers/ChatGPTProcessor.py | 72.5% |
| backend/llm_fetchers/UseCaseProcessor.py | 11.9% |
| backend/service_fetchers/services.py | 3.5% |
| frontend/api_handler.py | 68.4% |
| frontend/bot.py | 27.2% |
| frontend/tts_stt.py | 23.5% |
| **Projekt** | **24.8%** |

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