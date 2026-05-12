# ND13/2023 Compliance Checklist - MedViet AI Platform

## A. Data Localization
- [ ] Patient data is stored only on infrastructure located in Vietnam.
- [ ] Backups are stored in Vietnam and encrypted at rest.
- [ ] Cross-border transfer, if any, is logged with purpose, destination, approval, and retention period.

## B. Explicit Consent
- [ ] Consent is collected before patient data is used for AI training.
- [ ] Users can withdraw consent and request deletion or exclusion from future training.
- [ ] Consent records include patient id, scope, timestamp, channel, and policy version.

## C. Breach Notification 72h
- [ ] Incident response runbook defines triage, containment, evidence collection, and notification owner.
- [ ] Automated alerts are configured for suspicious API access and anomalous data export.
- [ ] Confirmed personal-data incidents are reported to the competent authority within 72 hours.

## D. DPO Appointment
- [ ] Data Protection Officer is appointed.
- [ ] DPO contact: dpo@medviet.example

## E. Technical Controls

| ND13 Requirement | Technical Control | Status | Owner |
|---|---|---|---|
| Data minimization | PII anonymization pipeline for names, CCCD, phone, email, address, birth date, and doctor name | Done | AI Team |
| Access control | RBAC policy for API roles plus OPA policy for authorization decisions | Done | Platform Team |
| Encryption | AES-256-GCM envelope encryption utility for sensitive fields and artifacts | Done | Infra Team |
| Audit logging | API access logs should capture user, role, resource, action, status, request id, and timestamp | Todo | Platform Team |
| Breach detection | Prometheus/Grafana alerts should monitor high-volume export, repeated 403/401, and unusual access windows | Todo | Security Team |
| Data retention | Retention policy should purge raw PII after approved processing and keep only anonymized training data | Todo | Data Governance |
| Right to erasure | Deletion workflow should remove raw record, revoke training eligibility, and record audit evidence | Todo | Product/Platform |

## F. Concrete Follow-up Work

- Audit logging: add FastAPI middleware that writes structured JSON logs to an append-only sink. Include token subject, resolved role, route, action, response code, and latency.
- Breach detection: add Prometheus counters for failed auth, denied authorization, and data export volume. Create Grafana alert rules for spikes and off-hours access.
- Data retention: schedule a daily cleanup job that deletes expired raw CSV/object-storage partitions after anonymized output passes validation.
- Right to erasure: maintain a suppression list keyed by patient_id so future training jobs exclude withdrawn records, even if historical anonymized data exists.
