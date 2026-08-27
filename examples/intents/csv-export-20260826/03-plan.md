# Plan: CSV export for reports

- **From spec:** `02-spec.md`
- **Status:** implemented

## Files that change

- `report/page.tsx`
- `report/export.ts` (new)
- `report/export.test.ts` (new)

## Order of work

1. Add `toCsv` helper with UTF-8 BOM.
2. Wire the button in `report/page.tsx`.
3. Add unit tests for `toCsv`.

## Risks

- Excel without BOM may mangle non-ASCII characters. Mitigated by adding BOM.

## Proof

- `npm test report/export.test.ts` passes.
- Playwright screenshot shows the button.