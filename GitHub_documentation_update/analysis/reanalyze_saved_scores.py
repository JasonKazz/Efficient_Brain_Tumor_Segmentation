"""Re-analyze preserved overlap scores; no MRI data or inference required."""
from pathlib import Path
from collections import defaultdict
from itertools import combinations
import csv
import hashlib
import json
import math
import statistics

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / 'artifacts' / 'original'
OUTPUT = ROOT / 'artifacts' / 'reanalysis' / 'overlap_summary.json'
COLS = [f'{metric}_{region}' for metric in ('dice', 'iou') for region in ('wt', 'tc', 'et')]


def patient(scan):
    return scan.rsplit('-', 1)[0]


def summarize(rows):
    means = {c: statistics.mean(float(r[c]) for r in rows) for c in COLS}
    by_patient = defaultdict(list)
    for r in rows:
        by_patient[patient(r['subject'])].append(r)
    return {
        'scans': len(rows), 'patients': len(by_patient),
        'mean': means,
        'sample_sd': {c: statistics.stdev(float(r[c]) for r in rows) for c in COLS},
        'macro_dice': statistics.mean(means[f'dice_{c}'] for c in ('wt', 'tc', 'et')),
        'macro_iou': statistics.mean(means[f'iou_{c}'] for c in ('wt', 'tc', 'et')),
        'equal_patient_weight_macro_dice': statistics.mean(
            statistics.mean(float(r[f'dice_{c}']) for r in scans)
            for scans in by_patient.values() for c in ('wt', 'tc', 'et')),
    }


def main():
    manifest = json.loads((ORIGINAL / 'manifest.json').read_text())
    for name, info in manifest.items():
        blob = (ORIGINAL / name).read_bytes()
        if hashlib.sha256(blob).hexdigest() != info['sha256']:
            raise ValueError(f'Original artifact checksum mismatch: {name}')
    splits = json.loads((ORIGINAL / 'splits.json').read_text())
    for name in ('train', 'val', 'test'):
        if len(splits[name]) != len(set(splits[name])):
            raise ValueError(f'Duplicate scan IDs within {name}')
    with (ORIGINAL / 'test_metrics_per_subject.csv').open(newline='') as f:
        rows = list(csv.DictReader(f))
    ids = [r['subject'] for r in rows]
    if len(ids) != len(set(ids)) or ids != splits['test']:
        raise ValueError('Test CSV IDs do not match the distinct ordered test split')
    for r in rows:
        for c in COLS:
            value = float(r[c])
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f'Invalid overlap score: {r["subject"]}, {c}')
    patients = {name: {patient(scan) for scan in splits[name]} for name in ('train', 'val', 'test')}
    overlap = {}
    for a, b in combinations(('train', 'val', 'test'), 2):
        if set(splits[a]) & set(splits[b]):
            raise ValueError(f'Exact scan overlap in {a}/{b}')
        overlap[f'{a}_{b}'] = len(patients[a] & patients[b])
    development = patients['train'] | patients['val']
    restricted = [r for r in rows if patient(r['subject']) not in development]
    result = {
        'analysis': 'Retrospective analysis of saved overlap scores; no new mask-level evaluation',
        'patient_definition': 'Scan identifier with final hyphen-delimited timepoint removed',
        'split_counts': {k: {'scans': len(splits[k]), 'patients': len(patients[k])} for k in patients},
        'shared_patient_counts': overlap,
        'original_test_rows': summarize(rows),
        'absent_from_train_and_val': summarize(restricted),
        'excluded_test_scan_ids': [r['subject'] for r in rows if patient(r['subject']) in development],
        'limitations': [
            'Original both-empty and undefined-overlap conventions remain in saved scores.',
            'Restricted cohort is retrospective and does not undo validation patient overlap.',
            'HD95 is not re-analyzed because failure status cannot be recovered reliably.',
            'Checkpoint contents and voxel predictions were not verified by this script.',
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2) + '\n')
    print(f'Saved {OUTPUT.relative_to(ROOT)}')
    for key in ('original_test_rows', 'absent_from_train_and_val'):
        q = result[key]
        print(f'{key}: {q["scans"]} scans, {q["patients"]} patients, macro Dice {q["macro_dice"]:.6f}, macro IoU {q["macro_iou"]:.6f}')


if __name__ == '__main__':
    main()
