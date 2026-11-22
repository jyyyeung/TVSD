COMMIT_MSG_HOOK = '\#!/bin/bash\nMSG_FILE=$$1\ncz check --allow-abort --commit-msg-file $$MSG_FILE'

setup-dev-env:
	pre-commit install
	echo $(COMMIT_MSG_HOOK) > .git/hooks/commit-msg
	chmod +x .git/hooks/commit-msg

bump:
	cz bump

bump-version-minor:
	cz bump --increment MINOR

bump-version-major:
	cz bump --increment MAJOR

bump-version-patch:
	cz bump --increment PATCH

bump-specific-version:
	cz bump $(VERSION)

fetch-tags:
	git fetch --tags

push-tag: fetch-tags
	git push --follow-tags origin main

install-deps:
	poetry install
	@command -v ffmpeg >/dev/null || echo "WARNING: ffmpeg not found on PATH (brew install ffmpeg)"
	@command -v yt-dlp >/dev/null || echo "WARNING: yt-dlp not found on PATH (brew install yt-dlp)"

test:
	poetry run pytest -q

smoke:
	poetry run python scripts/smoke.py

smoke-offline:
	poetry run python scripts/smoke.py --offline
