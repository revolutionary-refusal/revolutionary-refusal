# Federal reconciliation integrity — investigation 004

**Date:** 2026-11-20  
**Hypothesis:** Financial consolidation or reconciliation adjustments may eliminate reported differences while underlying transactions remain unmatched. This is a *testable risk*, not an established hidden software bug or proof of missing cash.

## Key verified finding — FY2025 consolidated financial statements
GAO reports that Treasury worked with agencies to reduce intragovernmental differences to amounts Treasury deemed immaterial, then **recorded an adjustment removing remaining differences with an offsetting adjustment to net cost**. GAO also reported that some entities could not accurately identify or fully reconcile all transactions with trading partners. This is an accounting/consolidation issue, not evidence of cash disappearance.

Primary: https://www.gao.gov/products/gao-26-108073 (see intragovernmental activity and balances section in full report)

## Other independently sourced findings
1. **GAO-26-109081 (Sep 2026)**: Material weaknesses in intragovernmental balances, properly balanced consolidation, and reconciliations of operating cost, budget deficit, and cash. Access recertification reports for Treasury Planning Analytics were inadequate to assess appropriate access. https://www.gao.gov/products/gao-26-109081
2. **GAO-26-107863 (May 2026)**: DHS financial modernization affecting ICE, FEMA, Coast Guard had unreliable schedules for two programs and uneven data migration/change-management planning. Does not establish a reconciliation bug. https://www.gao.gov/products/gao-26-107863
3. **GAO-26-108044 (Jun 2026)**: FY2025 reported estimated improper payments $186bn, incomplete program coverage. Improper ≠ fraudulent. https://www.gao.gov/products/gao-26-108044
4. **GAO-26-109100 (Jul/Aug 2026)**: 15/20 selected federally funded state-administered programs lacked documented evidence of both fraud risk identification and likelihood assessment. https://www.gao.gov/products/gao-26-109100
5. **GAO-05-407 (2005)**: GAO warned that some categories of material intragovernmental differences did not require detailed explanations. Historical, not proof of current noncompliance. https://www.gao.gov/assets/gao-05-407.pdf
6. **Treasury Intragovernmental Business Rules (Jun 2026)**: Require trading-partner agreement catalog and documentation of differences including amounts, affected accounts, rationale, and communication status. https://tfx.treasury.gov/media/51/download?inline=
7. **Treasury G-Invoicing guide**: Accounting posting logic alone does not ensure trading partners agree on timing and amounts. https://fiscal.treasury.gov/accounting/us-standard-general-ledger-ussgl/resources-g-invoicing-program-guide
8. **GAO FISCAM 2026**: Current audit framework for information system controls; relevant to logs, permissions, data integrity, and application controls. https://www.gao.gov/products/gao-26-108633

## Concrete audit test
- Obtain original agency-level transaction and trading-partner datasets, GTAS submission versions, quarterly scorecards, and year-end consolidation journal entries.
- For each elimination entry: record date, amount, debit/credit accounts, reason code, preparer, approver, source evidence, materiality threshold, and subsequent reversal.
- Independently match buyer and seller entries by agreement, invoice, transaction ID, amount, period, and Treasury settlement.
- Compare pre-adjustment unmatched balances to post-adjustment published balances; quantify *explained*, *unexplained*, and *immaterial but untraced* differences separately.
- Test access permissions, change logs, override activity, automated exception-clearing rules, and operator training/competence.
- Separate book-only adjustments from actual outlays and bank/Treasury settlements.

## Status
**Confirmed:** GAO documents reconciliation weaknesses and consolidation adjustments.  
**Unconfirmed:** Automated silent-clearing defect, unauthorized entries, missing funds, deliberate concealment, or debt understatement.  
**Next evidentiary requirement:** Transaction-level adjustment schedules and independent Treasury settlement records.

Do not interpret a balanced ledger as proof of complete or accurate underlying records.
