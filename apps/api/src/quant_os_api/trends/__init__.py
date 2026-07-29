"""Google Trends Intelligence — relative, sampled, normalized 0–100 indices.

Non-negotiable caveats (surface everywhere):
- Never treat scores as absolute search volume.
- Never compare separate exports without shared comparison context or anchors.
- Region and related-query channels are independent signals.
"""

from __future__ import annotations

CAVEATS = [
    "Google Trends is a relative 0–100 index within the selected time and geography — not absolute search volume.",
    "Values are sampled and can vary slightly across repeated pulls; we average repeats and expose confidence.",
    "Terms pulled in the same request are normalized relative to each other; preserve query-group context.",
    "Sparse or frequently-zero series are flagged unreliable and down-weighted in the Search Demand Score.",
    "Trends is a confirmatory alt-data channel — combine with satellite, app, pricing, and hiring signals.",
]

QUALITY_BADGES = ("high", "medium", "low", "unreliable")
