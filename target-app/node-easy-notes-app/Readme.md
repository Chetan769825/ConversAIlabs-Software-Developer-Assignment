# EasyNotes Application

Build a Restful CRUD API for a simple Note-Taking application using Node.js, Express and MongoDB.

## Steps to Setup

1. Install dependencies

```bash
npm install
```

2. Run Server

```bash
node server.js
```

You can browse the apis at <http://localhost:3000>

## Organise and search notes

Notes accept an optional `tags` array. Tags are trimmed, lowercased, deduplicated,
and validated. Existing clients may omit tags.

`GET /notes` retains its array response and accepts:

- `q`: case-insensitive title/content search (maximum 200 characters)
- `tag` or comma-separated `tags`: tag filtering (`tags` uses AND semantics)
- `sortBy`: `createdAt`, `updatedAt`, or `title`
- `order`: `asc` or `desc`
- `page` and `limit`: positive integers; limit is capped at 100

When pagination is requested, `X-Total-Count`, `X-Page`, and `X-Limit` headers
carry metadata without breaking the existing response shape. `GET /notes/tags`
returns tag usage counts. See `examples/api.http` for runnable requests.

## Tests

```bash
npm test
```

Tests use Jest, Supertest, and an in-memory MongoDB; no local database is required.

## Tutorial
You can find the tutorial for this application at [The CalliCoder Blog](https://www.callicoder.com) -

<https://www.callicoder.com/node-js-express-mongodb-restful-crud-api-tutorial/>
