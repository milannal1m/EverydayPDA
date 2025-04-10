
# EverydayPDA

## Table of Contents

1. [Coverage](#coverage)
2. [API](#api)
3. [Docker](#docker)
4. [GIT](#git)

## Coverage

![Coverage](https://img.shields.io/badge/Coverage-70.3%25-brightgreen)

| Datei | Coverage (%) |
|---|---|
| backend/UseCases.py | 100.0% |
| backend/api/answer_processor.py | 100.0% |
| backend/api/data_filler.py | 100.0% |
| backend/api/database.py | 75.0% |
| backend/api/database_utils.py | 14.3% |
| backend/api/models.py | 100.0% |
| backend/api/summary_generator.py | 95.1% |
| backend/api/usecase_handler.py | 96.2% |
| backend/llm_fetchers/ChatGPTProcessor.py | 90.0% |
| backend/llm_fetchers/UseCaseProcessor.py | 83.3% |
| backend/service_fetchers/services.py | 41.6% |
| frontend/api_client.py | 98.5% |
| frontend/bot.py | 100.0% |
| frontend/command_handlers.py | 100.0% |
| frontend/main.py | 84.6% |
| frontend/message_handlers.py | 92.7% |
| frontend/pref_config.py | 100.0% |
| frontend/pref_handler.py | 59.8% |
| frontend/speech_utils.py | 100.0% |
| frontend/start_handler.py | 75.0% |
| **Projekt** | **70.3%** |

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