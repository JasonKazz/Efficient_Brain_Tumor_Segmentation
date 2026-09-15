# Known issues and interpretation of the original experiment

Status date: September 14, 2026. This is a documentation and saved-score analysis update, not a corrected model-evaluation release. The preprint has not yet been revised. Historical repository reference: commit `2a837337964a276c294751b44764cd71798fad61`.

## Patient independence

The original procedure split scan folders rather than grouping repeated timepoints by patient. Removing the last hyphen-delimited timepoint component yields 1,133 patient prefixes across 1,251 scans. This interpretation is consistent with [organizer clarification](https://www.synapse.org/Synapse:syn53708249/discussion/threadId=11262).

| Partition pair | Shared patients |
|---|---:|
| Train–validation | 28 |
| Train–test | 24 |
| Validation–test | 4 |

No exact scan ID is shared, and no patient occurs in all three partitions. However, 28/188 test scans belong to patients present in development. Related-patient exposure can make evaluation optimistic; the artifacts do not identify the amount of inflation. This is not evidence that the listed test masks were directly used in training.

Restricting existing test scores to patients absent from development leaves 160 scans from 158 patients. This retrospective analysis is informative but cannot undo overlap affecting validation loss, threshold selection, or checkpoint selection. A new grouped development experiment is a distinct future experiment, not a change that can be made by relabeling the old split.

## Overlap aggregation

The original aggregate Dice/IoU path skips both-empty masks and uses MONAI's default exclusion of empty ground truth. The per-scan table assigns one to both-empty agreement and zero to other undefined overlap reductions. An outer check that prediction or ground truth is present does not disable the metric's internal exclusion rule. See [MONAI 1.5.0 Dice](https://github.com/Project-MONAI/MONAI/blob/1.5.0/monai/metrics/meandice.py) and [IoU source](https://github.com/Project-MONAI/MONAI/blob/1.5.0/monai/metrics/meaniou.py).

Thus the original aggregate ET Dice 0.870287 and IoU 0.799916 do not average all 188 saved rows. Those row means are 0.853150 and 0.785026. Regional means and sample SDs must use the same rows. The README reports arithmetic saved-row summaries; the original aggregate file is preserved as evidence, not relabeled as corrected output.

Saved-row IoU agrees with Dice/(2−Dice) within approximately 9e-8. This is an internal arithmetic check, not independent verification of masks. Actual empty-reference and empty-prediction identities require mask-level checks.

## Boundary distances

Five ET cases have saved Dice zero and HD95 zero, and one also has this TC pattern. Undefined surface distances were not consistently preserved: reductions can exclude them or produce zero, and subsequent conversion cannot restore missing status. See [MONAI reduction utilities](https://github.com/Project-MONAI/MONAI/blob/1.5.0/monai/metrics/utils.py) and [HD95 source](https://github.com/Project-MONAI/MONAI/blob/1.5.0/monai/metrics/hausdorff_distance.py).

The original mean HD95 is not a valid comprehensive boundary estimate. Neither re-averaging all stored distances nor removing zeros provides a justified correction. Re-evaluation needs explicit handling and counts for both-empty, prediction-empty-only, reference-empty-only, and both-present masks. Original unit spacing also requires verification against image geometry before interpreting distances as millimeters.

## Validation, thresholds, and checkpoint selection

The three-channel validation metrics use `include_background=False`, omitting WT at index zero. The singleton-channel regional test metrics do not drop their only foreground channel, so this does not invalidate WT test scores by the same mechanism. The training Dice loss is separate from the MONAI reporting metric.

Epoch 49 is the maximum both of the recorded validation Dice and the arithmetic mean of separately logged WT/TC/ET validation Dice over all 50 epochs. This limited check preserves the recorded winner. It does not establish the best checkpoint under a newly corrected scoring protocol.

The threshold-search objective likewise omits WT, so the retained WT threshold 0.25 is not evidence of successful WT optimization. Threshold state is not automatically restored on resumption. The retained JSON alone does not establish which thresholds were used in every historical validation epoch. Test evaluation independently uses fixed 0.5 thresholds.

Resumption restores model, optimizer, scheduler, and scaler states, but not random-number or threshold states. The best-score variable resets. The available log ranking check does not show a changed final winning epoch, but exact continuation is not established.

## Input order, figures, and missing checkpoints

The public training order is `t1c, t1n, t2f, t2w`. The public figures notebook's prediction/timing path swaps the last two modalities. The privately supplied edited figures notebook fixes this order, but retained outputs do not prove the provenance of the paper's predictions. The figure path also uses default CUDA FP16 autocast and `>0.5`, whereas test evaluation uses BF16 and `>=0.5`.

The figure loader can silently continue with randomly initialized weights when the requested checkpoint is missing. Do not interpret that output as trained-model inference. A maintained version should fail visibly on missing required weights.

The public architecture PDF incorrectly depicts depth reduction; code uses `(1,2,2)` pooling and preserves depth. Historical validation plots inherit the metric limitations above. The original HD95 distribution plot additionally hides 17 class-case observations above its axis limit. These plots are not corrected boundary evidence.

## Timing and comparative claims

The saved total-time median is 11.863 s. The approximately 11.2 s figure corresponds to loading/normalization; the forward subsection median is 0.582 s. The workload includes reference-mask loading and excludes sigmoid, thresholding, and output writing. Paths use mounted Drive, with no documented local-SSD staging or cache protocol. This is not complete-inference latency or a matched efficiency comparison.

The original whole-region metrics and internal cohort differ from [BraTS 2023 lesion-wise evaluation](https://github.com/rachitsaluja/BraTS-2023-Metrics). Published numerical comparisons do not establish superiority. No controlled ablation, repeated-seed study, or verified augmentation comparison supports causal claims about instance normalization, full-volume inputs, or omission of augmentation. The active final configuration has no augmentation.

## What has and has not been done

Completed for this update: artifact inspection, independent split/score analysis, and documentation of known limitations.

Pending: checkpoint inspection, original image/spacing verification, corrected mask-level evaluation, prediction regeneration, implementation fixes, tested environment, and preprint revision. None is implied to be complete by this documentation update.

The original experiment remains useful as implementation experience and descriptive segmentation evidence. Its clean patient-independent performance, boundary accuracy, and comparative superiority have not been established.
