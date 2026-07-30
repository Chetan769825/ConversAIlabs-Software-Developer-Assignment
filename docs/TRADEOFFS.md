# Trade-offs

- **Regex vs text search:** escaped case-insensitive regex is simple and supports
  substring matching without an index migration, but it scans at scale. Atlas Search
  or a designed text index is the production evolution.
- **Tags vs folders:** tags support overlapping organization with one optional field;
  folders add hierarchy, movement semantics, and more compatibility questions.
- **Custom state machine vs framework:** explicit Python stages are auditable and easy
  to test. A framework could add integrations but also hides control flow.
- **Bounded vs unlimited autonomy:** two passes limit cost and damage. Complex fixes
  may stop for human intervention.
- **Compatibility vs response redesign:** arrays remain the default and pagination
  uses headers, avoiding a breaking envelope migration.
- **Dependency update vs migration:** Mongoose is updated for maintained runtime and
  test compatibility, while Express, CommonJS, routes, and controller structure stay.
