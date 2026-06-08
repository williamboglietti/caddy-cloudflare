# Caddy avec le module DNS Cloudflare (DNS-01 ACME challenge).
# La version Caddy est injectée par la CI depuis le tag git (ex: v2.11.4 -> 2.11.4).
ARG CADDY_VERSION=2.11.4

FROM caddy:${CADDY_VERSION}-builder AS builder
RUN xcaddy build --with github.com/caddy-dns/cloudflare

FROM caddy:${CADDY_VERSION}
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
