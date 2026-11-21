#!/usr/bin/env python3
"""Summarize Trivy findings without turning findings into a release gate."""
import argparse
import json
import os
import sys


def findings(report, only_unfixed):
    if not isinstance(report, dict) or ("Results" not in report and "SchemaVersion" not in report):
        raise ValueError("rapport Trivy invalide")
    rows = set()
    for result in report.get("Results") or []:
        for vuln in result.get("Vulnerabilities") or []:
            if vuln.get("Severity") not in ("HIGH", "CRITICAL"):
                continue
            fixed = vuln.get("FixedVersion") or ""
            if only_unfixed and fixed:
                continue
            rows.add((vuln["Severity"], vuln.get("PkgName", "?"), vuln["VulnerabilityID"], vuln.get("InstalledVersion", "?"), fixed))
    return sorted(rows, key=lambda row: (row[0] != "CRITICAL", row[1], row[2]))


def annotation_text(text):
    return str(text).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def cell(text):
    return str(text).replace("|", "&#124;").replace("\r", " ").replace("\n", " ")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("report")
    parser.add_argument("--label", required=True)
    parser.add_argument("--only-unfixed", action="store_true")
    args = parser.parse_args()
    with open(args.report, encoding="utf-8") as handle:
        rows = findings(json.load(handle), args.only_unfixed)
    title = "HIGH/CRITICAL sans correctif" if args.only_unfixed else "HIGH/CRITICAL détectées"
    for severity, package, identifier, version, fixed in rows:
        message = f"{identifier} ({severity}) : {package} {version} ; correctif : {fixed or 'aucun indiqué'}"
        print(f"::warning title={annotation_text(args.label)}::{annotation_text(message)}")
    lines = [f"### {cell(args.label)} — {title} : {len(rows)}", ""]
    if rows:
        lines += ["| Sévérité | Paquet | CVE | Version | Correctif |", "|---|---|---|---|---|"]
        lines += ["| " + " | ".join(cell(value or "aucun indiqué") for value in row) + " |" for row in rows]
    else:
        lines.append("Aucune.")
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as summary:
        summary.write("\n".join(lines) + "\n")
    print(f"{args.label} : {len(rows)} résultat(s), signalés sans blocage.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Rapport Trivy illisible : {error}", file=sys.stderr)
        sys.exit(1)
