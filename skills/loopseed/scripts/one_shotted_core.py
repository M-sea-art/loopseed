"""Public control-plane API for LoopSeed One-Shotted mode."""

from one_shotted_bootstrap import initialize
from one_shotted_defects import record_defect
from one_shotted_evidence import record_gate_result
from one_shotted_finalize import finalize
from one_shotted_gates import add_gate
from one_shotted_status import status
from one_shotted_transition import transition
from one_shotted_types import OneShottedError
from one_shotted_validate import validate

__all__ = [
    "OneShottedError",
    "add_gate",
    "finalize",
    "initialize",
    "record_defect",
    "record_gate_result",
    "status",
    "transition",
    "validate",
]
