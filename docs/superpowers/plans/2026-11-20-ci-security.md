# CI et surveillance des images Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement and verify each task.

**Goal:** Surveiller les images publiées et protéger les modifications tout en conservant ARM.

**Architecture:** Les scans de candidates restent bloquants pour les vulnérabilités corrigibles ; un rapport partagé signale les autres. Un workflow séparé scanne quotidiennement Docker Hub et GHCR sur les deux architectures. Un contrôle final agrège la classification du diff et la CI applicable.

**Tech Stack:** GitHub Actions, Trivy, Python, Dependabot.

**Spec:** docs/superpowers/specs/2026-11-20-ci-security-design.md

## Global Constraints

- Préserver les publications multiarchitecture et la politique Trivy existante.
- Ne jamais autoriser une erreur ou un contrôle absent à produire un succès CI.

## Tasks

- [ ] Tester puis implémenter la classification documentaire et le rapport Trivy.
- [ ] Ajouter Dependabot, le scan quotidien et le contrôle final des PR ; documenter.
- [ ] Vérifier tests, workflow et CI distante ; publier la PR actualisée.
- [ ] Activer et vérifier les alertes Dependabot et les règles GitHub après validation de la CI.
