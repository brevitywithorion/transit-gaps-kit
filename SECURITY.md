# Security

This kit is a local analysis CLI. It does not deploy a public site by itself.

- Never commit API keys (`CENSUS_API_KEY`), tokens, or `.env` files.
- Do not copy Cloudflare Pages functions, Turnstile secrets, or feedback inboxes from the Lawrence origin site into this repository.
- GTFS feeds may include agency phone/email fields; they are not stored in git (`runs/` is gitignored). Example prose should not restate personal contacts.
- Optional r5py / Java workloads should run offline on your machine; do not expose them as unauthenticated network services.

Report security issues privately to the repository owner.
