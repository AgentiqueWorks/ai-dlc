# Intent: Payment audit logging

- **ID:** payment-audit-20260827
- **Author:** beto (PM)
- **Status:** approved
- **Date:** 2026-08-27

## Problem

PCI compliance requires an immutable audit log of payment events.

## Proposed outcome

Every payment event emits an audit record with actor, action, entity, and timestamp.

## Affected users and systems

- Payments service
- Audit log store

## Constraints

- PII must not appear in logs.
- Change requires security sign-off.

## Open questions

- Should the log be async via a queue? (Answered: yes, Kafka outbox.)