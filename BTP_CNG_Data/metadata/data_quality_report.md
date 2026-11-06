# Data quality and provenance report

## Repairs to the inherited data

All 46 original data, metadata, script and log files are preserved byte-for-byte under `quarantine/legacy_main/`, with SHA-256 checksums in `metadata/legacy_file_manifest.csv`.

1. The 2,293 inherited revision rows contain 2,018 same-price observations, 265 candidate changes and 10 initial observations. Source observations and candidate changes are now separate. Neither is falsely called a verified effective revision.
2. Inherited observation dates had been copied into effective/publication fields without evidence. Those claims are retained as legacy fields; active verified effective/publication fields remain missing.
3. Ten November 2026 partial monthly targets are quarantined. All other constructed targets also remain unfinalized because the true dated price paths are not established.
4. Exponential VAHAN registrations and their derived index are quarantined. Active observed registration values are missing until a real export is acquired.
5. Hardcoded APM ceilings treated as monthly prices and unsupported VAT timelines are quarantined. Official gas notices are acquired separately with different price concepts kept distinct.
6. GDP is retained as annual, in constant 2015 USD according to the World Bank indicator. It is not monthly GDP, current INR GDP, a quarterly source or a verified historical release vintage.
7. Backward-filled fuel prices, undocumented continuity and fixed publication assumptions remain in quarantine. Yahoo monthly FX closes are labelled proxy bar closes, never monthly means. The World Bank Europe gas series is not automatically TTF; Japanese LNG import prices are not JKM.
8. The 125 Wayback entries are archive locators, not news articles. They are retained separately; archive capture times do not establish original publication times.
9. Corporate metadata now references downloaded source documents. A nonempty index does not establish historical exchange release time or semantically validated procurement metrics.
10. The legacy 100% result is superseded by content comparisons, checksums, source/type checks, arithmetic conflicts, chronology checks and explicit blocked completion gates. Missing months are not filled to make a completeness metric pass.

## Newly exposed target-source conflicts

IGL's official chronology includes missing cells and negative values that appear to be changes rather than absolute prices. They are retained as source cells and excluded from positive absolute-price claims. The workbook's 6 March 2024 revision label differs from independent coverage describing a 7 March 2024, 06:00 IST effective change. No automatic date shift has been applied. The same-date Noida observation on 24 March 2022 conflicts: IGL reports 61.58 while the inherited secondary response reports 62.58 INR/kg. Other same-date matches do not validate the unobserved intervals between them.

## Time, geography and licensing

Unknown publication timestamps remain null. Document signature/issue dates, report reference periods, HTTP Last-Modified headers and extraction timestamps are different fields. A later revised vintage cannot be assumed available at a historical forecast origin. City, GA, district, RTO, operator, national and global records retain their own grain. IGL Kanpur and CUGL Kanpur, or IGL Gurugram and HCG, must not be collapsed without authorization-boundary evidence.

Public access does not establish a redistribution license. Source licensing status is item-specific and unresolved where terms were not verified. Institutional product existence and a library search page do not prove current campus entitlement. No authentication, paywall or CAPTCHA was bypassed.

## Outstanding limitations

The semantic extraction of all numerical report tables, complete city target paths, original public-release histories, observed vehicle exports and broad historical H2 coverage remain incomplete. Source-discovery matches and retained document rows are not treated as a fully validated dataset. Review `data_inventory.csv`, `manual_collection_queue.csv`, `pngrb_component_conflicts.csv`, `revision_effective_date_conflicts.csv` and `logs/stage3_validation.json` for specific records and next actions.
