# Original artifacts and retrospective analysis

`original/` contains exact copies of the files supplied for the September 14, 2026 audit. Checksums are in `original/manifest.json`. These artifacts were supplied separately from the public repository snapshot and do not by themselves prove an immutable link to a particular historical notebook revision or checkpoint.

| File | Meaning and limitation |
|---|---|
| `splits.json` | Historical scan-level split. Contains patient overlap; do not reuse as a grouped split. |
| `eval_thresholds.json` | Retained threshold values. Does not prove restoration or usage history. |
| `epoch_metrics.csv` | Historical training/validation log. Recorded multichannel means omit WT. |
| `test_metrics.csv` | Original aggregate output. Preserved despite aggregation/HD95 issues. |
| `test_metrics_per_subject.csv` | Original per-scan output. Filename uses “subject,” but rows are scans and patients repeat. HD95 failure information is unreliable. |

`reanalysis/overlap_summary.json` is new, separate output from the standard-library analysis script. The original files are never overwritten.

The script averages saved Dice/IoU columns by scan, reports sample standard deviations using N−1, and averages regional means with equal WT/TC/ET weights. It also reports macro Dice with equal patient weighting, by first averaging repeated scans for each patient. Restriction to patient prefixes absent from train and validation is retrospective. Saved zero and one overlap values remain unchanged.

No MRI data or predictions are included. No model inference, revised thresholding, boundary re-evaluation, or new training is performed by this analysis. The source checksums, cohort counts, excluded IDs, and explicit averaging units make the arithmetic inspectable without implying full experimental reproduction.
