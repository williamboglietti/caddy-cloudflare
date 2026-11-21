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
# Le commit ciblé de Smallstep Certificates adopte Crypto v0.92.0 et go-jose/v4.
# Le remplacement s'applique uniquement à Certificates v0.30.2.
RUN xcaddy build v${CADDY_VERSION} \
    --with github.com/caddy-dns/cloudflare@${CLOUDFLARE_DNS_VERSION} \
    --replace github.com/smallstep/certificates@v0.30.2=github.com/smallstep/certificates@v0.30.3-0.20261105204752-cddde30af36e \
    --replace github.com/go-jose/go-jose/v4=github.com/go-jose/go-jose/v4@v4.1.9 \
    --replace golang.org/x/net=golang.org/x/net@v0.62.0

# Vérifie le binaire de chaque plateforme avant de l'embarquer dans l'image.
RUN set -e; \
    if [ "${CADDY_VERSION}" = "2.11.9" ]; then \
      build_info="$(go version -m /usr/bin/caddy)"; \
      printf '%s\n' "$build_info" | grep -F 'go.step.sm/crypto'; \
      if printf '%s\n' "$build_info" | grep -Fq 'github.com/go-jose/go-jose/v3'; then \
        echo 'go-jose/v3 est encore présent dans le binaire Caddy 2.11.9.' >&2; \
        exit 1; \
      fi; \
    fi

FROM ${CADDY_RUNTIME_IMAGE}
# Met à jour les paquets Alpine, même si l'image officielle de Caddy vient
# d'être publiée avant la mise à disposition des correctifs dans sa base.
RUN apk upgrade --no-cache
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
