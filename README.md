# Full-volume 3D U-Net for brain tumor segmentation

An independent research project implementing a four-modality, full-volume 3D U-Net for overlapping glioma-region segmentation on BraTS 2023 Adult Glioma data.

> **Research status — September 14, 2026:** The released preprint has not yet been revised to incorporate a retrospective audit. That audit identified patient overlap across the original scan-level split, inconsistent overlap-metric aggregation, and unreliable treatment of undefined boundary distances. The original headline results should not be interpreted as a fully patient-independent, consistently scored performance estimate. The notebooks are historical implementations with known issues, not a corrected reproduction pipeline. Read [KNOWN_ISSUES.md](KNOWN_ISSUES.md) before using the results or running the notebooks.

## Project overview

The project uses four MRI channels in this order:

1. Post-contrast T1 (`t1c`)
2. Native T1 (`t1n`)
3. T2-FLAIR (`t2f`)
4. T2 (`t2w`)

The targets are three overlapping binary regions:

- **WT:** whole tumor, all nonzero annotation labels.
- **TC:** tumor core, labels 1 and 3.
- **ET:** enhancing tumor, label 3.

The model has three downsampling stages, channel widths 64/128/256/512, instance normalization, and 21,708,163 trainable parameters. Pooling and transposed convolutions use `(1,2,2)`, preserving array depth. The active configuration uses full volumes, positive-voxel intensity standardization, and a combined BCE-with-logits and batch-pooled soft Dice loss. No augmentation or ensemble is active in the supplied final training configuration.

The saved record contains 50 training epochs with batch size two and AdamW. The test output identifies epoch 49 as the loaded checkpoint. These are reconstructed historical details; checkpoint contents and original voxel predictions were not inspected in the audit.

## What the results currently establish

The original split contains 875 training, 188 validation, and 188 test scans. Distinct scan IDs do not guarantee distinct patients: repeated timepoints cross partitions. Twenty-eight test scans belong to patients represented in training or validation.

The following values were recomputed from the **saved per-scan overlap scores**. They are not new model predictions or a repeat of mask-level metric computation.

| Saved-score analysis | Scans / patients | WT Dice | TC Dice | ET Dice | Macro Dice | Macro IoU |
|---|---:|---:|---:|---:|---:|---:|
| Original test partition | 188 / 186 | 0.9246 | 0.8931 | 0.8532 | 0.8903 | 0.8329 |
| Retrospective subset: patients absent from training and validation | 160 / 158 | 0.9264 | 0.8837 | 0.8418 | 0.8840 | 0.8265 |

Each regional mean weights scans equally; macro values average the three regional means equally. The original both-empty overlap convention remains in these saved scores. The restricted subset does not undo patient overlap in validation or establish a prospectively patient-grouped experiment. Differences between the cohorts also reflect changed case composition and do not measure the causal size of leakage bias.

The original aggregate Dice 0.8960 and IoU 0.8379 use a different empty-region population from the all-row summaries above. The original HD95 headline of approximately 3.855 is **not endorsed as a valid all-case boundary estimate**. No corrected boundary summary is available yet. Results are not directly comparable to BraTS 2023 challenge submissions using different cohorts and lesion-wise scoring.

## Repository contents

| Path | Role |
|---|---|
| `BraTS_3D_UNet.ipynb` | Historical training and evaluation notebook; known metric, split, and resumption limitations. |
| `BraTS_3D_UNet_PaperFigures.ipynb` | Historical analysis and figure notebook; input-channel order and prediction provenance require correction/verification. |
| `unet_architecture.pdf` | Historical public diagram; its depth reduction is inconsistent with the `(1,2,2)` implementation. |
| `KNOWN_ISSUES.md` | Scientific interpretation, implementation limitations, and pending corrections. |
| `artifacts/original/` | Unmodified CSV/JSON artifacts supplied for the audit, with checksums. These were retained privately before this documentation package. |
| `artifacts/reanalysis/` | Separately generated saved-score summaries and excluded test-scan IDs. |
| `analysis/reanalyze_saved_scores.py` | Reproduces the retrospective overlap summaries without MRI volumes, weights, or third-party Python packages. |
| `ENVIRONMENT.md` | Historical software evidence and limits of reproduction. |

## Reproduce the saved-score analysis

From the repository root, with Python 3.9 or later:

```bash
python3 analysis/reanalyze_saved_scores.py
```

The script reads the preserved split and per-scan metrics files, verifies their recorded checksums, checks scan membership, reconstructs patient-prefix overlap, and writes `artifacts/reanalysis/overlap_summary.json`. It does not run either notebook, change model weights, or modify the original artifacts.

The artifact documentation explains the averaging units and limitations: [artifacts/README.md](artifacts/README.md).

## Training and model evaluation

The historical notebooks use Google Colab/Drive paths and GPU computation. The original MRI data must be obtained through the [BraTS organizers](https://www.synapse.org/Synapse:syn51156910/wiki/621282) under their access requirements. MRI volumes are not included here. The original trained checkpoint is retained by the author but is not distributed in this update.

The notebooks currently require manual path/environment configuration and contain the issues documented below. They are provided for inspection of the project, not as a claim that a fresh run reproduces the original results. In particular, the figure loader can continue with random weights when a checkpoint is missing; verify weight loading before any prediction is interpreted. Do not use the historical splitting procedure for a new patient-independent experiment.

See [ENVIRONMENT.md](ENVIRONMENT.md) for recorded software versions. A tested, corrected training/evaluation entry point and a frozen environment remain future work.

## Next corrections

1. Verify original checkpoint metadata, image geometry, modality order, and prediction provenance.
2. Re-evaluate existing weights with explicit empty-region rules, valid boundary-distance handling, and patient overlap excluded from the evaluation cohort.
3. Correct the maintained notebooks and document behavior changes separately from the historical experiment.
4. Revise the preprint and release verified artifacts and reproduction instructions.

A new grouped training/validation experiment would be necessary to evaluate the full development pipeline under a prospectively patient-independent design. No retraining is needed merely to recompute saved-score summaries or correct documentation.

## Authorship and assistance

Jason Kasnicki developed the original project. An AI assistant supported the retrospective artifact audit, saved-score analysis, and documentation drafting. This assistance did not independently reproduce training or mask-level evaluation. The author remains responsible for the project's claims and future corrections.

## License

The project code is covered by the existing [MIT license](LICENSE). That license does not grant rights to redistribute the BraTS dataset; dataset use is governed by the organizers' terms.
