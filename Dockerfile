# Caddy avec le module DNS Cloudflare (DNS-01 ACME challenge).
# La CI injecte la version officielle de Caddy, ou celle du tag (v2.11.4 -> 2.11.4).
ARG CADDY_VERSION=2.11.4
ARG CLOUDFLARE_DNS_VERSION=latest

FROM caddy:${CADDY_VERSION}-builder AS builder
ARG CLOUDFLARE_DNS_VERSION
RUN xcaddy build --with github.com/caddy-dns/cloudflare@${CLOUDFLARE_DNS_VERSION}

FROM caddy:${CADDY_VERSION}
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
