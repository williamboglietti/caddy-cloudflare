#!/usr/bin/env bash
set -euo pipefail

run_suffix=${1:?usage: scan_candidates.sh RUN_SUFFIX}
scan_status=0

# Complete both architecture scans before returning a blocking result.
for arch in amd64 arm64; do
  candidate="caddy-cloudflare:scan-$run_suffix-$arch"
  trivy image --platform "linux/$arch" --scanners vuln --vuln-type os,library \
    --severity MEDIUM,LOW --exit-code 0 "$candidate" || scan_status=1
  trivy image --platform "linux/$arch" --scanners vuln --vuln-type os,library \
    --severity HIGH,CRITICAL --exit-code 1 "$candidate" || scan_status=1
done

exit "$scan_status"
