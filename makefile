COMMIT_MSG_HOOK = '\#!/bin/bash\nMSG_FILE=$$1\ncz check --allow-abort --commit-msg-file $$MSG_FILE'

init: setup-dev-env
	@cd web && mkdir -p _vendor static
	poetry install
	poetry run python ./web/manage.py migrate
	poetry run python ./web/manage.py collectstatic --noinput

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