# Security Scan Status

## Fixed Dependency Finding

- `urllib3` is pinned in `requirements.txt` as `urllib3>=2.7.0`.
- This remediates the reported `urllib3 2.5.0` findings, including the issue
  that requires at least `urllib3 2.7.0`.
- `Brotli` and `brotlicffi` are not installed in the checked environment, so no
  Brotli package upgrade is required unless Brotli support is added later.

## Manual Tooling Still Required

`trufflehog` is a standalone CLI and is not installed by `pip install -r
requirements.txt`. Install or run it separately before generating
`reports/trufflehog_report.txt`.

If using Docker, run TruffleHog from the repository root, not from the
`medviet-governance` subdirectory, because `.git` lives one directory above the
project folder:

```powershell
cd D:\Work\Day24-Track02-Lab-Assignment
$repo = (Get-Location).Path
docker run --rm -v "${repo}:/repo" trufflesecurity/trufflehog:latest git file:///repo --only-verified *> medviet-governance\reports\trufflehog_report.txt
```

For dependency audit, prefer auditing the lab requirements rather than the
machine-wide Python environment:

```powershell
cd D:\Work\Day24-Track02-Lab-Assignment\medviet-governance
$env:PYTHONIOENCODING = "utf-8"
pip-audit -r requirements.txt --desc on *> reports\pip_audit_report.txt
```
