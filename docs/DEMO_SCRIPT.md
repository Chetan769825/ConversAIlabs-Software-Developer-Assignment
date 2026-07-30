# 2–3 Minute Demo Script

Recording link: **GOOGLE_DRIVE_RECORDING_LINK_HERE**

1. Show the assignment root and the separated `agent/`, `tests/`, and `target-app/`.
2. Show the original architecture via `git -C target-app/node-easy-notes-app show HEAD:server.js`.
3. Run `python main.py inspect --repo target-app/node-easy-notes-app`.
4. With `.env` configured, run:
   `python main.py run --repo target-app/node-easy-notes-app --request "Improve the application so users can better organise and search their notes." --dry-run`.
5. Point out the printed repository discoveries and typed plan.
6. Show `git -C target-app/node-easy-notes-app diff --stat` and the model, controller,
   validation helper, route, and tests.
7. Run `python -m pytest`, then
   `cd target-app/node-easy-notes-app && npm test`.
8. Start MongoDB and `npm start`, then execute requests from `examples/api.http`:
   create a tagged note, search, filter, paginate, and list tag counts.
9. Show `git diff` and `python main.py show-last-run`.
10. Close on the safety boundaries and the recording-link placeholder above.
