import importlib.util
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    path = ROOT / "scripts" / f"{name}.py"
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DocumentationTests(unittest.TestCase):
    def test_allowed_and_disallowed_documentation(self):
        policy = load("classify_changes")
        self.assertIsNotNone(policy, "change classifier must exist")
        self.assertEqual(policy.classify([("docs/guide.md", "100644")]), "docs")
        self.assertEqual(policy.classify([("docs/image.png", "100644")]), "docs")
        self.assertEqual(policy.classify([("README.md", "100644")]), "docs")
        self.assertEqual(policy.classify([("Dockerfile", "100644")]), "full")
        with self.assertRaises(ValueError):
            policy.classify([("docs/run.sh", "100755")])
        with self.assertRaises(ValueError):
            policy.classify([("docs/file.md", "120000")])
        self.assertEqual(policy.classify([]), "full")


class TrivyReportTests(unittest.TestCase):
    def test_filter_deduplicate_and_escape_warnings(self):
        report = load("trivy_report")
        self.assertIsNotNone(report, "Trivy report must exist")
        data = {"Results": [{"Vulnerabilities": [
            {"Severity": "HIGH", "PkgName": "pkg", "VulnerabilityID": "CVE-1", "InstalledVersion": "1"},
            {"Severity": "HIGH", "PkgName": "pkg", "VulnerabilityID": "CVE-1", "InstalledVersion": "1"},
            {"Severity": "CRITICAL", "PkgName": "bad\n::error::x", "VulnerabilityID": "CVE-2", "InstalledVersion": "1", "FixedVersion": "2"},
            {"Severity": "LOW", "PkgName": "x", "VulnerabilityID": "CVE-3", "InstalledVersion": "1"},
        ]}]}
        unfixed = report.findings(data, only_unfixed=True)
        self.assertEqual(len(unfixed), 1)
        self.assertEqual(unfixed[0][2], "CVE-1")
        all_findings = report.findings(data, only_unfixed=False)
        self.assertEqual(len(all_findings), 2)
        self.assertNotIn("\n", report.annotation_text(all_findings[0][1]))

    def test_bad_report_is_rejected(self):
        report = load("trivy_report")
        self.assertIsNotNone(report, "Trivy report must exist")
        with self.assertRaises(ValueError):
            report.findings({}, only_unfixed=False)


class CandidateScanTests(unittest.TestCase):
    def test_scan_selection_and_blocking_status(self):
        with tempfile.TemporaryDirectory() as directory:
            trivy = Path(directory) / "trivy"
            trivy.write_text(r"""#!/bin/sh
printf '%s\n' "$*"
case " $* " in
    *" --platform $FAIL_PLATFORM "*" --exit-code 1 "*) exit 1 ;;
esac
""")
            trivy.chmod(0o755)

            for selected in (None, "amd64", "arm64"):
                architectures = (selected,) if selected else ("amd64", "arm64")
                command = ["bash", str(ROOT / "scripts/scan_candidates.sh"), "123-1"]
                if selected:
                    command.append(selected)
                for platform in ("", "linux/amd64", "linux/arm64"):
                    with self.subTest(selected=selected, failure=platform):
                        result = subprocess.run(
                            command,
                            env={
                                **os.environ,
                                "PATH": f"{directory}:{os.environ['PATH']}",
                                "FAIL_PLATFORM": platform,
                            },
                            capture_output=True,
                            text=True,
                        )
                        should_block = any(platform == f"linux/{arch}" for arch in architectures)
                        self.assertEqual(result.returncode, int(should_block), result.stderr)
                        expected = []
                        for arch in architectures:
                            prefix = f"image --platform linux/{arch} --scanners vuln --vuln-type os,library"
                            image = f"caddy-cloudflare:scan-123-1-{arch}"
                            expected.extend((
                                f"{prefix} --severity MEDIUM,LOW --exit-code 0 {image}",
                                f"{prefix} --severity HIGH,CRITICAL --exit-code 1 {image}",
                            ))
                        self.assertEqual(result.stdout.splitlines(), expected)


if __name__ == "__main__":
    unittest.main()
