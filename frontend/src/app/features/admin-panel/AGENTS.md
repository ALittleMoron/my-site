# Admin Panel Instructions

These rules apply to every file under `frontend/src/app/features/admin-panel/`.

## Access and Rendering

- Keep admin-panel routes protected and CSR-only. Enforce the matching backend role boundary; do
  not expose private admin responses through SSR or the hydration transfer cache.
- Keep narrower owner-only and owner/admin workspaces behind their dedicated child guards instead
  of treating every admin-panel role as equivalent.

## Agent Client Administration

- Keep lifecycle and audit views in the owner-only admin contour backed by the owner-guarded
  `/api/admin/agent-clients` API. Do not broaden them to admin/moderator roles or public routes.
- Registration accepts only a client-generated CSR, name, and explicit least-privilege scopes.
  Never request, upload, cache, or render a client private key. Make the one-time certificate return
  clear and require explicit confirmation for permanent client revocation.
- Present agent-created matrix items as drafts requiring human review. Do not add direct private
  Agent API/MCP execution, publishing, generic CRUD, structure changes, URL fetching, shell/HTTP
  controls, or imply a claim grants broader authority.

## Knowledge People

- Keep People under the owner/admin-protected CSR routes
  `/admin-panel/knowledge/people` and `/admin-panel/knowledge/people/:id`.
- Use explicit typed People forms/models for person details, birthday, tags, relationships, photo,
  and attachments. Do not introduce a schema-driven universal knowledge form renderer; future
  knowledge types should own their typed feature facade and interaction design.
- Read private photos/downloads only through protected blob responses and revoke every object URL
  when it is replaced or no longer displayed. People descriptions may use the shared sanitized
  Markdown editor, but image paste/drop/picker uploads must remain disabled because inline public
  media would bypass the private knowledge-file workflow.
