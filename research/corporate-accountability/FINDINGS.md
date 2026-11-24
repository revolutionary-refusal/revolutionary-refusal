# Findings register

Curated, reviewed entries. The collector never writes to this file. Every entry is dated, cites primary documents by clean URL, and carries exactly one status:

| Status | Meaning |
|---|---|
| **PROVEN** | Established by the cited primary document's own words, or by a court ruling or final order. Scope is limited to what the document states. A company's filing proves what the company disclosed, not that the disclosure is complete. |
| **ALLEGATION** | Asserted by a party, regulator or complainant and not adjudicated or admitted. |
| **HYPOTHESIS** | The investigator's inference. Stated so it can be tested; it lists what evidence would confirm or refute it. |
| **OPEN QUESTION** | Something the record does not answer. |

Corrections are appended with a date, never silently overwritten. Entries are ordered by record number, not importance.

Investigator for entries F-001 to F-011: Claude (Anthropic model), working in this repository at the owner's direction. **Conflict of interest, disclosed:** Claude is made by Anthropic, which is a subject of this investigation (F-001 to F-003, F-009, F-010). Anthropic entries were written to the same evidentiary standard as the others, and readers should check them against the cited filing.

---

### F-001 · PROVEN · D1 D2 D4 · Anthropic, Amazon, Google
**Recorded 2026-11-24 (Asia/Jerusalem).** Anthropic's final IPO prospectus says that after the offering, Amazon and Google will hold 1,936,452,353 and 1,774,959,745 shares of non-voting Class N stock: **14.6% and 13.4% of Anthropic's outstanding capital stock.** If Amazon's convertible notes converted in full without the ownership cap (a cap Amazon "has elected not to waive in connection with this offering"), Amazon would hold **23.6%** of outstanding capital stock. The same filing says notes under an Amazon note purchase agreement can be repaid, at Amazon's election, "by set-off against amounts Amazon owes the Company under certain commercial agreements." On an IPO or listing, the notes convert at the lower of $2.0928 (2023 agreement) or $5.0478 (2024 agreement) per share and the offering price. The offering price was $83.00.
- Source: Anthropic, PBC, Form 424B4, filed 2026-11-19, accession 0001628280-26-074944. https://www.sec.gov/Archives/edgar/data/2130357/000162828026074944/anthropicpbc-424b4.htm
- Verify: open the filing and search for "14.6%", "23.6%" and "set-off".
- Does not show: the dollar value of Anthropic's commercial payments to Amazon or Google. That needs the related-person transactions section and the financial statement notes (next step).

### F-002 · PROVEN · D1 D2 · Anthropic, Google, NVIDIA, AMD, Broadcom, Micron, Microsoft, TSMC
**Recorded 2026-11-24.** In a private placement that closes immediately after the IPO, seven companies agreed to buy **$26.0 billion** of Anthropic's non-voting Class N stock at the $83.00 IPO price, with no underwriting fees: Google about $10.0B (funding part of a previously committed obligation under its 2026 note purchase agreement), **NVIDIA about $10.0B**, AMD about $2.5B, Broadcom about $1.0B, Micron about $1.0B, Microsoft about $1.0B and TSMC Partners about $500M. The same prospectus reports that after 31 December 2025 Anthropic entered into new or amended compute and infrastructure agreements with **aggregate future minimum payment obligations of about $417 billion**, "primarily" leases for compute equipment and data centres and purchase commitments with cloud providers, plus an estimated **$125–150 billion** more for capacity delivered 2028–2031.
- Source: as F-001. Search "aggregate of $26.0 billion" and "$417 billion".
- Does not show: which counterparties hold the $417B of obligations, or how much flows back to the placement investors.

### F-003 · PROVEN · D6 D1 · Anthropic
**Recorded 2026-11-24.** Anthropic is a Nasdaq "controlled company". One Class F share, held by a Founder LLC whose initial members are the seven co-founders, carries **50.1% of total voting power** on matters put to stockholders generally. One Class T share, held by the Long-Term Benefit Trust, elects and removes the directors who make up a majority of the board. Class N shares (held mainly by strategic partners, including Amazon and Google) have no vote except where the law requires one, and convert to voting Class A shares when sold to an unaffiliated party.
- Source: as F-001. Search "50.1%", "Founder LLC", "Class T".
- OPEN QUESTION: as a controlled company, which Nasdaq governance requirements does Anthropic say it will rely on exemptions from? (Not yet extracted.)

### F-004 · PROVEN · D1 D2 D4 · Microsoft, OpenAI
**Recorded 2026-11-24.** Microsoft's quarterly report says it holds an equity-method investment in OpenAI representing **about a 24% interest on an as-converted basis**, and treats OpenAI as a related party under ASC 850. For the quarter ended 30 September 2026, Microsoft recorded **$10.0 billion of revenue from commercial arrangements with OpenAI**, including revenue-sharing payments. Accounts receivable from OpenAI were $7.2B at 30 September 2026, up from $6.0B at 30 June 2026. Microsoft's total funding commitments for the investment are $13.0B, of which $12.0B had been funded. Microsoft also reports that it holds rights to OpenAI's intellectual property, including models and infrastructure.
- Source: Microsoft Corp., Form 10-Q for the quarter ended 2026-09-30, filed 2026-10-28, accession 0001193125-26-436133. https://www.sec.gov/Archives/edgar/data/789019/000119312526436133/msft-20260930.htm
- Verify: search the filing for "approximate 24".
- Does not show: OpenAI's own figures. OpenAI is not an SEC registrant; the ledger tracks Form D filings by vehicles that raise money to invest in OpenAI (lead).

### F-005 · PROVEN + OPEN QUESTION · D2 D6 · NVIDIA
**Recorded 2026-11-24.** On 11 November 2026 NVIDIA's board accepted Jensen Huang's resignation as President, CEO and director, named CFO Colette Kress interim CEO, and appointed Harvey C. Jones the first board chair. On 17 November the board created a standing National Security and Export Control Oversight Committee; NVIDIA's national security and trade compliance teams now report to it. On 22 November the board reinstated Mr. Huang. In its 23 November announcement the board said it was "satisfied with respect to Mr. Huang's candor and ability to lead NVIDIA", and that it "received input from senior levels of the United States government, and based on that input, the Board is confident that Mr. Huang's reinstatement poses no national security risk." Neither 8-K gives a reason for the resignation.
- Sources: NVIDIA Form 8-K filed 2026-11-12 (accession 0001045810-26-000082) https://www.sec.gov/Archives/edgar/data/1045810/000104581026000082/nvda-20261111.htm and its exhibit https://www.sec.gov/Archives/edgar/data/1045810/000104581026000082/nvidiaannouncesceotransiti.htm · Form 8-K filed 2026-11-23 (accession 0001045810-26-000090) https://www.sec.gov/Archives/edgar/data/1045810/000104581026000090/nvda-20261122.htm · NVIDIA press releases https://nvidianews.nvidia.com/news/nvidia-board-reinstates-jensen-huang-as-president-ceo-and-board-director and https://nvidianews.nvidia.com/news/nvidia-board-of-directors-establishes-national-security-and-export-control-oversight-committee
- OPEN QUESTIONS: Why did Mr. Huang resign? What candor concern did the board examine? Who in the U.S. government gave input to a private company's board about its CEO, through what channel, and on what record?
- HYPOTHESIS (unverified, not a finding): the resignation was connected to national-security or export-control compliance. Basis: the board's own wording and the committee's timing. It would be confirmed or refuted by a later 10-Q/10-K, a proxy statement, litigation, or a regulator's statement.

### F-006 · PROVEN + OPEN QUESTION · D5 D1 · NextEra Energy, Dominion Energy
**Recorded 2026-11-24.** On 19 November 2026 DOJ's Antitrust Division closed its investigation of NextEra's $66.8B acquisition of Dominion **without a consent decree**. DOJ says it "remained concerned" about the deal's effect on ISO New England's capacity market (the incentive to retire still-economic plants to raise capacity payments). It closed the matter after the companies told FERC they would "commit, without qualification, to comply" with the ISO-NE Internal Market Monitor's proposal. Under that proposal, the monitor may review any plant the merged firm wants to deactivate for five years from the May 2028 capacity auction, and deactivation is barred if the plant still has economic value. The commitment applies whether or not FERC makes it a condition of approval.
- Source: https://www.justice.gov/opa/pr/justice-departments-statement-closing-its-investigation-nexteras-acquisition-dominion
- OPEN QUESTIONS: Who can enforce a commitment made in a FERC filing if FERC does not adopt it as a condition? Did DOJ examine PJM, where the portfolios also overlap?
- Lead (unreviewed): the same DOJ page links statements closing reviews of FOX/Roku (6 Nov 2026) and Vistra/Cogentrix (30 Oct 2026). Whether DOJ now closes merger reviews on commitments rather than decrees is a D6 question to test.

### F-007 · ALLEGATION · D4 D6 · Amazon
**Recorded 2026-11-24.** The FTC and 22 states filed an updated, less-redacted complaint alleging that Amazon used deceptive and unfair practices to secretly inflate prices in its online search-advertising auction to meet corporate financial targets. These are allegations in a pending case; nothing here is adjudicated.
- Source: FTC press release, 5 November 2026. https://www.ftc.gov/news-events/news/press-releases/2026/11/new-details-emerge-amazon-ads-auction-rigging-case
- Next: link the docket once it appears in the CourtListener feed; record Amazon's response.

### F-008 · PROVEN (procedural) · D4 D1 · Alphabet / Google
**Recorded 2026-11-24.** The UK CMA designated Google with strategic market status in general search and search advertising in October 2025. It consulted on conduct requirements on 28 January 2026, then on an updated "user choice" conduct requirement (open 23 September to 9 October 2026). The outcome page was updated on 23 November 2026. This records procedural steps only; the requirement's final terms and Google's compliance are not yet recorded.
- Source: https://www.gov.uk/government/consultations/googles-general-search-services-proposed-user-choice-conduct-requirement

### F-009 · PROVEN · D6 · OpenAI, Anthropic, NVIDIA
**Recorded 2026-11-24.** Federal lobbying reported for the third quarter of 2026 (July–September) under the Lobbying Disclosure Act:

| Client | In-house filing (company's own report) | Outside firms (sum of firms' reported income) | Filings |
|---|---|---|---|
| Anthropic | $2,110,000 | $930,000 | 10 |
| NVIDIA | $2,150,000 | $460,000 | 6 |
| OpenAI | $1,530,000 | $310,000 | 4 |

Do not add the columns: LDA rules can count payments to outside firms inside a company's own expense figure. Method (reproducible): `https://lda.gov/api/v1/filings/?client_name=<name>&filing_year=2026&filing_period=third_quarter`, keeping filings whose client name contains the company name. Each filing's URL is in the ledger (`source: lda-lobbying`).
- Does not show: what was lobbied for. Issue codes are in each filing's `meta.issues`; the specific bills and agencies are in the filing text.

### F-010 · PROVEN (with limits) · D2 · Anthropic, OpenAI, NVIDIA, xAI
**Recorded 2026-11-24.** USAspending shows three Department of Health and Human Services contracts to Anthropic, PBC, all starting 26 October 2026, with obligated amounts of $4,842,000, $3,573,000 and $585,000 ($9.0M in total), plus a Smithsonian contract for $114,000. In the same 60-day window, no contract matched OpenAI, NVIDIA or xAI by recipient name. That shows only an absence within this window: awards made through resellers or under other legal names would not appear.
- Sources: https://www.usaspending.gov/award/CONT_AWD_7571TE27C00002_7571_-NONE-_-NONE- · https://www.usaspending.gov/award/CONT_AWD_7571TE27C00003_7571_-NONE-_-NONE- · https://www.usaspending.gov/award/CONT_AWD_7571TE27C00004_7571_-NONE-_-NONE- · https://www.usaspending.gov/award/CONT_AWD_33330227CF0010440_3300_-NONE-_-NONE-
- Obligated amounts are not money paid.

### F-011 · PROVEN (count) / ALLEGATION (content) · D3 D4 · Experian, TransUnion, Equifax
**Recorded 2026-11-24.** The CFPB Consumer Complaint Database lists 768,147 complaints received in October 2026, as retrieved on 23 November 2026. The three national credit bureaus account for 696,314 of them (**90.6%**): Experian 271,119; TransUnion 224,377; Equifax 200,818. The next largest are LexisNexis at 4,192 and Capital One at 3,333. The count of complaints is a fact; each complaint is an unverified allegation, and later publication raises the counts.
- Source: https://www.consumerfinance.gov/data-research/consumer-complaints/search/?date_received_min=2026-10-01&date_received_max=2026-10-31&tab=Trends
- HYPOTHESIS: concentrated complaint volume against three firms reflects a structural chokepoint (consumers cannot switch bureaus) more than ordinary service failure. Test: compare bureau complaint shares with the response categories ("closed with explanation" vs relief) and with CFPB and FTC enforcement history.

---

## Leads queued for review
- Who holds the ~$417B of Anthropic compute obligations (F-002)? Check the exhibit 10.x agreements in the S-1 filings.
- OpenAI fundraising vehicles: dozens of Form D filings by SPVs named for OpenAI (`sec-edgar-fulltext`, query `"OpenAI"`, forms D). Map sponsors, sizes and dates.
- NVIDIA's own investments in AI developers it supplies: NVIDIA's latest 10-Q and 13F filings (filed 2026-11-16) set against F-002.
- DOJ merger closures without decrees (F-006 lead).
