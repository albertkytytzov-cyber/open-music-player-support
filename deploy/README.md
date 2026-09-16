# Open Music Player site deployment

The public source of truth is this repository. Production runs as a separate
static container on the Performarc server and joins the existing reverse-proxy
network without exposing another public port.

Production layout:

- `/home/weekend/openmusic-site/releases/<release>` — immutable release directories
- `/home/weekend/openmusic-site/current` — symlink to the active release
- `/home/weekend/openmusic-site/runtime` — Compose and Nginx configuration
- `openmusic-site` — isolated static Nginx container
- `openmusic.performarc.app` — Caddy virtual host and public HTTPS endpoint

Each deployment uploads a new release and switches the `current` symlink only
after local validation. Rollback points the symlink to the preceding release.
The existing Performarc application, API, database, mail and VPN services are
not part of this Compose project.
