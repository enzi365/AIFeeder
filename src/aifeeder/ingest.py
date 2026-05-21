"""RSS ingestion. Fetch sources, parse feeds, write new items to DB.

One source failing does not stop others — errors are caught per-source
and recorded against the source row (consecutive_failures, last_error_*).
"""
from __future__ import annotations

# Implementation lands after the AI prompt A-checkpoint —
# the CLI iterates on the prompt with stdout first, then we persist.
