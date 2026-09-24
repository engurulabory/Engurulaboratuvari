# OSi Self-Hosted GitHub Runner — Commissioning Contract v1

## STATE

Prepared optional external-check execution adapter for ENGÜRÜ Mac Engineer™.

## ROLE

GitHub keeps repository / PR / check / merge authority.

OSi supplies Mac ARM64 compute.

The local operator remains fully usable when GitHub Actions is unavailable.

## LABEL CONTRACT

```text
self-hosted
macOS
ARM64
enguru-mac
```

## SECURITY

Registration token is entered interactively with hidden input.

The commissioning command does not write the token to source, Evidence or shell history.

Runner release is downloaded from the official `actions/runner` GitHub release and requires a published SHA-256 digest before extraction.

## SERVICE

The official runner service helper is used so the listener can survive Terminal closure and user-session restart according to the runner's supported macOS service behavior.

## COMMAND

```bash
zsh governance/mac-engineer/COMMISSION_OSI_GITHUB_RUNNER.command
```

The user obtains the short-lived repository registration token from:

`engurulabory/enguru-mac-engineer → Settings → Actions → Runners → New self-hosted runner`

The token remains local and private.

## AUTHORITY

A self-hosted GitHub check is valid external CI Evidence because GitHub creates the workflow/check record while OSi supplies compute.

If account-level GitHub Actions execution remains unavailable, local OSi engineering continues and external confirmation stays HOLD until the GitHub service gate clears.
