#!/usr/bin/env bash
set -euo pipefail

run_suffix=${1:?usage: scan_candidates.sh RUN_SUFFIX [amd64|arm64]}
architectures=(amd64 arm64)
case ${2:-} in
  '') ;;
  amd64|arm64) architectures=("$2") ;;
  *) printf 'Architecture non prise en charge : %s\n' "$2" >&2; exit 2 ;;
esac
scan_status=0

# Collect all requested scan results before returning a blocking status.
for arch in "${architectures[@]}"; do
  candidate="caddy-cloudflare:scan-$run_suffix-$arch"
  trivy image --platform "linux/$arch" --scanners vuln --vuln-type os,library \
    --severity MEDIUM,LOW --exit-code 0 "$candidate" || scan_status=1
  trivy image --platform "linux/$arch" --scanners vuln --vuln-type os,library \
    --severity HIGH,CRITICAL --exit-code 1 "$candidate" || scan_status=1
done

exit "$scan_status"
