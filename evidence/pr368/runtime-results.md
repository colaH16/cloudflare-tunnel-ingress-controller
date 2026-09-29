# Real Cloudflare Tunnel HTTP comparison

The same Ingress UID and specification were retained across the image switch. The five tunnel rules below were read back from the Cloudflare API. All 20 requests returned HTTP 200 in each final run. Echo response bodies identify the selected backend.

| Ingress path / type | Before tunnel regex | After tunnel regex |
|---|---|---|
| `/wp-admin/` / Prefix | `/wp-admin/` | `^/wp-admin(/\|$)` |
| `/admin` / Prefix | `/admin` | `^/admin(/\|$)` |
| `/v1.0` / Prefix | `/v1.0` | `^/v1\.0(/\|$)` |
| `/` / Prefix | `/` | `^/` |
| `/legacy/(admin\|login)$` / ImplementationSpecific | `/legacy/(admin\|login)$` | `/legacy/(admin\|login)$` |

| Request path | Before | After |
|---|---|---|
| `/` | PUBLIC | PUBLIC |
| `/wp-admin` | PUBLIC | ADMIN |
| `/wp-admin/` | ADMIN | ADMIN |
| `/wp-admin/edit.php` | ADMIN | ADMIN |
| `/foo/wp-admin/` | ADMIN | PUBLIC |
| `/wp-admin-other/` | PUBLIC | PUBLIC |
| `/WP-ADMIN/` | PUBLIC | PUBLIC |
| `/v1.0` | LITERAL | LITERAL |
| `/v1.0/users` | LITERAL | LITERAL |
| `/v1X0` | LITERAL | PUBLIC |
| `/prefix/v1.0` | LITERAL | PUBLIC |
| `/legacy/admin` | ADMIN | ADMIN |
| `/legacy/login` | ADMIN | ADMIN |
| `/foo/legacy/admin` | ADMIN | ADMIN |
| `/legacy/admin/edit` | ADMIN | PUBLIC |
| `/admin` | ADMIN | ADMIN |
| `/admin/` | ADMIN | ADMIN |
| `/admin/settings` | ADMIN | ADMIN |
| `/admin-tools` | ADMIN | PUBLIC |
| `/prefix/admin` | ADMIN | PUBLIC |

ImplementationSpecific remains an unanchored regex, so `/foo/legacy/admin` still intentionally matches.

The first new-host warm-up attempt included one HTTP 530 response. An immediate post-rollout request also saw the previous rule while configuration propagation was in progress. These attempts are recorded separately in `test-observations.json`; the complete comparison runs started after the test host and generated rule set were ready.
