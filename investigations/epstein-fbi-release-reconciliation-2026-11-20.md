# Epstein FBI release reconciliation ledger

Created: 2026-11-20. **Status: preliminary; not a finding of intentional concealment.**

## Public index baseline
- FBI Vault Epstein collection: https://vault.fbi.gov/jeffrey-epstein — 22 linked parts, Part 22 labelled Final (verified 2026-11-20).
- Separate FBI review-of-investigative-holdings collection: https://vault.fbi.gov/records-regarding-the-review-of-the-investigative-holdings-related-to-jeffrey-epstein/
- DOJ internal inventory source to inspect: https://www.justice.gov/oip/media/1470366/dl?inline= (large document; not fully retrieved in this audit pass).

## Records requiring exact identifier matching
| Lead | Reported evidence | Present release location | Classification | Next verification |
|---|---|---|---|---|
| FBI serial 407, file 50D-NY-3027571 | Earlier research described as temporarily inaccessible in Sentinel | Not matched | Unresolved | Verify inventory wording, pages, and later release |
| FBI serial 411, same file | Same | Not matched | Unresolved | Verify inventory and release |
| 2,080 pending-upload pages | Earlier research described March 2025 reconciliation | Not matched | Unresolved | Verify source inventory, avoid double-counting |
| 16 files removed from DOJ website | Earlier reporting alleged removal in Dec 2025 | Not matched | Unresolved | Capture exact filenames, hashes, restored status |
| 2022 FOIA withheld pages | Court records describe historical withholding | Current public match not performed | Historical withholding | Compare specific FOIA processing IDs with later productions |

**Classification definitions:** publicly located / officially withheld / inaccessible / unexplained absence / pending verification. A missing public match is not proof of destruction or suppression.

## Protocol
1. Preserve original document URL, exact filename, page count, release date, SHA-256 when obtained.
2. Extract FBI case number, serial number, Bates identifier, page spans, attachments, and redaction codes.
3. Deduplicate across FBI Vault and DOJ productions by content hash plus document identifier; account for renamed files.
4. For absent records, identify lawful withholding notices and later republications before calling the absence unexplained.
5. Never expose victim identifiers or personal data in public GitHub notes.

## Audit log
2026-11-20: FBI Vault index independently opened and confirmed to contain 22 linked parts. DOJ inventory PDF URL could not be read through web viewer due to file size; earlier specific inventory claims remain unverified in this pass.

Sources: https://vault.fbi.gov/jeffrey-epstein ; https://www.justice.gov/oip/media/1470366/dl?inline=


---

## Four-pass review addendum — 2026-11-20
Revision note: FBI Vault index of 22 parts independently rechecked. Original DOJ inventory memorandum was too large to fully reopen here; serial-level assertions remain pending original-page verification. Uploaded PDFs' hashes and page counts appear in consolidated review.
**Controlling cross-thread revision:** [Four-pass evidence audit](cross-thread-four-pass-revision-2026-11-20.md). Prior content retained for historical auditability; interpret in light of the correction.
