.PHONY: test inspect validate
test:
	python -m pytest
	cd target-app/node-easy-notes-app && npm test
inspect:
	python main.py inspect --repo target-app/node-easy-notes-app
validate:
	python main.py validate --repo target-app/node-easy-notes-app
