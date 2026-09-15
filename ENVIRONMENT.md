# Environment evidence and reproduction status

The historical notebooks were developed for a Google Colab GPU environment with Google Drive paths. They are not currently a tested one-command reproduction pipeline.

| Evidence | Recorded version or setting |
|---|---|
| Training notebook installation output | PyTorch 2.6.0; MONAI 1.5.0; TorchIO 0.20.22 |
| Figures notebook installation output | PyTorch 2.9.0; TorchIO 0.21.0 |
| GPU identification | A100; exact memory variant not independently verified |
| Training/test autocast | BF16 in the primary implementation |
| Figure/timing autocast | Default CUDA FP16 |
| Performance settings | Channels-last, TF32, cuDNN benchmarking |

Installation output is not an immutable environment record for every later cell. The notebooks install unpinned packages and the retained outputs include dependency conflicts. A lockfile written now would describe a newly tested environment, not necessarily the original experiment.

The split random state is 42. The public general seed is 1337; the edited training attachment uses 42 with identical retained training outputs. The original model seed is unresolved. Saved optimizer and scheduler state do not establish exact continuation when RNG and threshold states are missing.

For the newly added `analysis/reanalyze_saved_scores.py`, only Python 3.9+ standard-library modules are required. Its successful execution validates saved-artifact arithmetic, not the historical GPU pipeline. A corrected GPU environment will be documented after testing; no speculative `requirements.txt` is provided in this update.
