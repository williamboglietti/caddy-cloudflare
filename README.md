# caddy-cloudflare

Image Docker [Caddy](https://caddyserver.com/) compilée avec le module
[`caddy-dns/cloudflare`](https://github.com/caddy-dns/cloudflare), pour résoudre
le challenge ACME **DNS-01** via l'API Cloudflare (certificats wildcard, domaines
sans exposition des ports 80/443).

- **Image** : `williamboglietti/caddy-cloudflare` (Docker Hub) et `ghcr.io/williamboglietti/caddy-cloudflare` (GHCR)
- **Architectures** : `linux/amd64`, `linux/arm64`
- **Tags** : `latest`, plus la version Caddy (`2.11.4`, `2.11`, `2`)

## Token Cloudflare

Crée un **API Token** Cloudflare (pas la Global API Key) avec la permission
`Zone / DNS / Edit` sur la ou les zones concernées, puis expose-le via la
variable d'environnement `CF_API_TOKEN`.

## Caddyfile

```caddyfile
example.com {
    tls {
        dns cloudflare {env.CF_API_TOKEN}
    }
    respond "Hello from Caddy + Cloudflare"
}
```

Pour un wildcard :

```caddyfile
*.example.com {
    tls {
        dns cloudflare {env.CF_API_TOKEN}
    }
}
```

## docker-compose.yml

```yaml
services:
  caddy:
    image: williamboglietti/caddy-cloudflare:latest
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"
    environment:
      CF_API_TOKEN: ${CF_API_TOKEN}
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config

volumes:
  caddy_data:
  caddy_config:
```

> Garde le volume `caddy_data` persistant : il contient les certificats et les
> clés de compte ACME. Le perdre force une réémission des certificats.

## Vérifier que le module est présent

```sh
docker run --rm williamboglietti/caddy-cloudflare:latest caddy list-modules | grep cloudflare
# -> dns.providers.cloudflare
```

## Licence

[MIT](LICENSE)
