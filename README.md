# MyFeedMemory
MyFeedMemory is an open-source AI tool that transforms saved LinkedIn posts into a searchable knowledge base. It uses LLMs to summarize, categorize, and enable semantic search over your personal feed.

## What this repo contains

- `CLAUDE.md` — project behavior guide and coding conventions.
- `.claude/settings.local.json` — local environment configuration for OpenRouter/Anthropic settings.
- `tests/` — test scripts, including the OpenRouter connectivity probe.
- `.venv/` — local Python virtual environment.
- `requirements.txt` — Python dependencies.

## Local setup

1. Create or activate the virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Install the package in editable mode:

```powershell
python -m pip install -e .
```

## Run the connectivity test

```powershell
python tests\test_openrouter_connection.py
```

## Run the LinkedIn fetch CLI

If you are in the repo root and have not installed the package, use:

```powershell
set PYTHONPATH=src
py -m myfeedmemory.cli.fetch_linkedin
```

After installing the package in editable mode, you can use either:

```powershell
py -m myfeedmemory.cli.fetch_linkedin
```

or the script entrypoint:

```powershell
myfeedmemory-fetch
```

or the root runner:

```powershell
py run.py
```

## Notes

- `CLAUDE.md` now uses the Andrej Karpathy style guide for coding and change discipline.
- If you want to add new skills or scripts, document them in `CLAUDE.md` and keep implementations minimal and reviewable.
