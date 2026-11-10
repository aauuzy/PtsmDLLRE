# detection

Holds the detector and YARA rules for the Potassium sample:

- `ptsm_detector.py` — a PE-gated, score-based classifier.
- `ptsm_executor.yar` — YARA rules for confirmed static signals.

Both are pending. They are written only after the analysis records signals in [`../docs/research/FINDINGS.md`](../docs/research/FINDINGS.md), so that every signature traces to evidence rather than to a guess. The intended approach is described in [`../docs/defense/DETECTION.md`](../docs/defense/DETECTION.md).
