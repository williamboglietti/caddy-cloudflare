# CI et surveillance des images

Objectif : conserver les images Caddy/Cloudflare multiarchitecture, rendre visibles les CVE non corrigées, surveiller chaque jour les images `latest` publiées, et exiger une CI adaptée sur les PR. La publication reste bloquée pour les HIGH/CRITICAL corrigibles.

Choix : conserver Alpine, la base officielle existante, plutôt que migrer sans comparaison probante ; scanner les images publiées séparément plutôt que reconstruire quotidiennement, afin de détecter de nouvelles CVE même sans nouvelle version. Les problèmes identifiés dans l'image publiée sont signalés sans republier ni modifier l'image. Les erreurs du scanner restent des échecs visibles.

Les PR purement documentaires passent une vérification légère ; seules les extensions autorisées sont admises sous `docs/`, sans lien symbolique. Les autres changements exécutent la compilation et les scans existants pour amd64 et arm64. Dependabot suit Docker et GitHub Actions chaque semaine. La protection de `main` exige une PR et `CI complete` après déploiement et vérification du contrôle.
