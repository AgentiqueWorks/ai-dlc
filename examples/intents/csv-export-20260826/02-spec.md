# Spec: CSV export for reports

- **From intent:** `01-intent.md`
- **Status:** approved

## Requirements

1. A "Download CSV" button appears next to the existing PDF button.
2. Clicking it downloads a `.csv` with the currently filtered report rows.
3. The CSV includes a UTF-8 BOM for Excel compatibility.
4. With zero rows, the file contains headers only.

## Design

- Add `toCsv(rows, columns)` in `report/export.ts`.
- Add a `<Button variant="secondary" onClick={downloadCsv}>` in `report/page.tsx`.
- Reuse the existing `/api/reports/data` endpoint.

## Areas of concern

- None after the BOM constraint was added.

## Acceptance criteria

- [ ] Button is visible in the UI.
- [ ] CSV download works for 1, 50, and 0 rows.
- [ ] Existing PDF export is unaffected.