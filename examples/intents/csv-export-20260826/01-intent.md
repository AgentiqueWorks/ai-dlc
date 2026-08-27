# Intent: CSV export for reports

- **ID:** csv-export-20260826
- **Author:** beto (PM)
- **Status:** approved
- **Date:** 2026-08-26

## Problem

Customers cannot export report data. Support has received 12 requests in the last month.

## Proposed outcome

Add a CSV export button to the `/reports` page. It should download the current filtered view as a `.csv` file.

## Affected users and systems

- Report users
- `report/page.tsx`
- `report/export.ts`

## Constraints

- Keep existing PDF export unchanged.
- No new backend service; use the existing report API.
- Empty data sets must not crash.

## Open questions

- Do we need UTF-8 BOM for Excel compatibility? (Answered: yes, add BOM.)