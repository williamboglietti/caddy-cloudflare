# Caddy avec le module DNS Cloudflare (DNS-01 ACME challenge).
# Caddy est compilé depuis sa release officielle, avec les images officielles
# builder et runtime les plus récentes disponibles comme environnement de base.
ARG CADDY_VERSION=2.11.4
ARG CADDY_BUILDER_IMAGE=caddy:2.11.4-builder
ARG CADDY_RUNTIME_IMAGE=caddy:2.11.4
ARG CLOUDFLARE_DNS_VERSION=latest

FROM ${CADDY_BUILDER_IMAGE} AS builder
ARG CADDY_VERSION
ARG CLOUDFLARE_DNS_VERSION
RUN xcaddy build v${CADDY_VERSION} \
    --with github.com/caddy-dns/cloudflare@${CLOUDFLARE_DNS_VERSION} \
    --replace github.com/go-jose/go-jose/v4=github.com/go-jose/go-jose/v4@v4.1.6 \
    --replace golang.org/x/net=golang.org/x/net@v0.60.0

FROM ${CADDY_RUNTIME_IMAGE}
# Met à jour les paquets Alpine, même si l'image officielle de Caddy vient
# d'être publiée avant la mise à disposition des correctifs dans sa base.
RUN apk upgrade --no-cache
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
