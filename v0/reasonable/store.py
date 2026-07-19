"""On-disk I/O for the Reasonable v0 data layer.

Two files are FROZEN by BUILD-SPEC.md §1 and live directly under the data
dir: `events.jsonl` (append-only log of successful writes only) and
`graph.json` (deterministic derived snapshot, rewritten wholesale after
every write and by `rebuild`).

One additional file, `audit.jsonl`, is NOT part of the frozen schema -- it's
a small implementation extension so `stats` can report the health signals
BUILD-SPEC.md §2 asks for ("self-agree attempts rejected", "duplicate-text
warnings") across CLI invocations. Rejected writes are, by definition, not
mutations, so they must never appear in events.jsonl; audit.jsonl is where
their existence is still observable. See graph.py --help / final report for
the full rationale.
"""
from __future__ import annotations

import contextlib
import fcntl
import json
import os
import signal
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

EVENTS_FILE = "events.jsonl"
GRAPH_FILE = "graph.json"
AUDIT_FILE = "audit.jsonl"
CONFIG_FILE = "config.json"
LOCK_FILE = ".lock"
DEFAULT_LOCK_TIMEOUT = 30.0


class LockTimeoutError(RuntimeError):
    """Raised when the data-dir write lock could not be acquired in time."""


class _LockAlarm(Exception):
    """Internal signal used to unwind a blocking flock() after a timeout."""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_data_dir(data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)


def _acquire_flock(fh, timeout: float, lock_path: Path) -> None:
    """Block on an exclusive fcntl.flock() of `fh`, but give up cleanly after
    `timeout` seconds instead of hanging forever or busy-spinning.

    fcntl.flock() has no native timeout, so on the (default) case of being
    called from the main thread of a POSIX process we impose one with
    SIGALRM: a real blocking syscall, unwound by a signal handler that turns
    the interrupt into a normal Python exception (PEP 475 does NOT retry the
    call because the handler raises). If SIGALRM isn't usable (non-main
    thread, or a platform without it) we fall back to a short-sleep polling
    loop -- not a hot spin -- bounded by the same deadline.
    """
    if hasattr(signal, "SIGALRM") and threading.current_thread() is threading.main_thread():
        def _on_alarm(signum, frame):
            raise _LockAlarm()

        previous_handler = signal.signal(signal.SIGALRM, _on_alarm)
        signal.setitimer(signal.ITIMER_REAL, timeout)
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        except _LockAlarm:
            raise LockTimeoutError(
                f"could not acquire the write lock on {lock_path} within {timeout:g}s "
                "-- another process is holding it (a concurrent writer, or a stuck one). "
                "If you're sure nothing else is writing, delete the .lock file and retry."
            ) from None
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)  # cancel the alarm
            signal.signal(signal.SIGALRM, previous_handler)
    else:
        deadline = time.monotonic() + timeout
        while True:
            try:
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return
            except OSError:
                if time.monotonic() >= deadline:
                    raise LockTimeoutError(
                        f"could not acquire the write lock on {lock_path} within {timeout:g}s "
                        "-- another process is holding it (a concurrent writer, or a stuck one). "
                        "If you're sure nothing else is writing, delete the .lock file and retry."
                    ) from None
                time.sleep(0.05)


@contextlib.contextmanager
def locked(data_dir: Path, timeout: float = DEFAULT_LOCK_TIMEOUT):
    """Exclusive advisory lock (POSIX `fcntl.flock` on `<data_dir>/.lock`)
    over the ENTIRE write critical section: read/fold current state ->
    validate -> append event (with its seq assignment) -> rebuild
    graph.json. Two concurrent writers serialize through this lock, so seq
    numbers stay unique and strictly increasing and events.jsonl never sees
    an interleaved/torn append.

    Blocking with a bounded wait: raises `LockTimeoutError` (a clear error,
    not a hang or a spin) if the lock isn't free within `timeout` seconds.
    Read verbs do not take this lock -- they only read the atomically
    replaced graph.json / append-only events.jsonl snapshot.
    """
    data_dir = Path(data_dir)
    ensure_data_dir(data_dir)
    lock_path = data_dir / LOCK_FILE
    fh = open(lock_path, "a+")
    try:
        _acquire_flock(fh, timeout, lock_path)
        try:
            yield
        finally:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
    finally:
        fh.close()


def read_events(data_dir: Path) -> list[dict]:
    path = Path(data_dir) / EVENTS_FILE
    if not path.exists():
        return []
    events = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            events.append(json.loads(line))
    events.sort(key=lambda e: e["seq"])
    return events


def append_event(data_dir: Path, event: dict) -> None:
    ensure_data_dir(Path(data_dir))
    path = Path(data_dir) / EVENTS_FILE
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True))
        f.write("\n")


def make_event(state: dict, agent: str, verb: str, payload: dict) -> dict:
    return {
        "seq": state["event_count"] + 1,
        "ts": now_iso(),
        "agent": agent,
        "verb": verb,
        "payload": payload,
    }


def write_graph_json(data_dir: Path, graph: dict) -> None:
    ensure_data_dir(Path(data_dir))
    path = Path(data_dir) / GRAPH_FILE
    tmp_path = path.with_suffix(".json.tmp")
    text = json.dumps(graph, sort_keys=True, indent=2, ensure_ascii=False)
    with tmp_path.open("w", encoding="utf-8") as f:
        f.write(text)
        f.write("\n")
    os.replace(tmp_path, path)


def read_graph_json(data_dir: Path) -> dict | None:
    path = Path(data_dir) / GRAPH_FILE
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def append_audit(data_dir: Path, agent: str, verb: str, status: str,
                  items: list[tuple[str, str]]) -> None:
    """Record rejected/warned write attempts for stats' health signals.
    `items` is a list of (tag, message) as returned by validate.py."""
    if not items:
        return
    ensure_data_dir(Path(data_dir))
    path = Path(data_dir) / AUDIT_FILE
    with path.open("a", encoding="utf-8") as f:
        for tag, message in items:
            rec = {
                "ts": now_iso(),
                "agent": agent,
                "verb": verb,
                "status": status,
                "tag": tag,
                "message": message,
            }
            f.write(json.dumps(rec, sort_keys=True))
            f.write("\n")


def read_audit(data_dir: Path) -> list[dict]:
    path = Path(data_dir) / AUDIT_FILE
    if not path.exists():
        return []
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def read_config(data_dir: Path) -> dict:
    path = Path(data_dir) / CONFIG_FILE
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_config(data_dir: Path, config: dict) -> None:
    """Persist `<data>/config.json` (PHASE2-SPEC.md §1: "config used must be
    recorded ... so rebuilds are reproducible from the log + flags" -- CLI
    flags like `rebuild --quorum 8` persist into this file's `"phase2"`
    block so every SUBSEQUENT write/rebuild, even ones that pass no flags of
    their own, keeps using the same phase-2 config, exactly like the
    existing `"assessment"` block already works). Callers must already hold
    `store.locked(data_dir)` -- same convention as `write_graph_json`."""
    ensure_data_dir(Path(data_dir))
    path = Path(data_dir) / CONFIG_FILE
    tmp_path = path.with_suffix(".json.tmp")
    text = json.dumps(config, sort_keys=True, indent=2, ensure_ascii=False)
    with tmp_path.open("w", encoding="utf-8") as f:
        f.write(text)
        f.write("\n")
    os.replace(tmp_path, path)


# --- id assignment -----------------------------------------------------
# All ids are derived purely from current fold-state counts, so assignment
# is itself deterministic and idempotent given a valid, ordered log.

def next_node_id(state: dict) -> str:
    return f"n{len(state['node_order']) + 1:03d}"


def next_edge_id(state: dict) -> str:
    return f"e{len(state['edge_order']) + 1:03d}"


def next_group_id(state: dict) -> str:
    return f"g{len(state['group_order']) + 1}"


def next_set_id(state: dict) -> str:
    return f"s{len(state['set_order']) + 1}"


def next_friction_id(state: dict) -> str:
    return f"f{len(state['frictions']) + 1}"


def next_phrasing_id(node: dict) -> str:
    return f"p{len(node['phrasings'])}"


def next_title_id(node: dict) -> str:
    return f"t{len(node['titles'])}"


def next_comment_id(state: dict) -> str:
    # FORUMS-SPEC.md §1: comment ids are global (c001, c002...), zero-padded
    # to 3 like nodes/edges -- not per-target, since a comment can target
    # either a node or an edge and replies must not collide with top-level
    # comments' numbering.
    return f"c{len(state['comment_order']) + 1:03d}"


def next_typing_id(edge: dict) -> str:
    # FORUMS-SPEC.md §1: typing ids are per-edge (ty1, ty2...), 1-based (no
    # ty0) since -- unlike phrasing p0/title t0 -- there is no auto-created
    # initial typing at draw-ground time.
    return f"ty{len(edge['typings']) + 1}"
