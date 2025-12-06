# app.py — SCPCE.5 enhanced CLI for the Persistent Context Engine
from __future__ import annotations
import sys
import json
import hashlib
import os
from typing import List

from pce import api
from pce.storage import MEMORY_FILE, load_all
from pce.schema import RecapFrame, ContextBundle

"""
───────────────────────────────────────────────────────────────────────────────
 Developer’s Note

 This system started as a personal tool — a way to force clarity, determinism,
 and traceability into long-running reasoning. But it was never meant to stay
 on a laptop.

 Transparent autonomy, auditable memory, and human-gated control systems matter.
 They require more than one engineer; they require people who understand why
 determinism and accountability must be built into the foundation, not bolted
 on later.

 If you're reading this because you're evaluating the architecture:
   - I build systems where every step is inspectable.
   - State is explicit, never magical.
   - Memory is accountable, never free-floating.
   - Safety and transparency aren't features — they're prerequisites.

 I'm ready to work with the teams who believe the same.
───────────────────────────────────────────────────────────────────────────────
"""

BANNER = """
===================================================
      SCPCE.5 — Persistent Context Engine CLI
===================================================
Commands:
  save                    - record a new interaction (user + assistant)
  load                    - reconstruct current reasoning state
  search <keyword>        - retrieve relevant memory frames
  tail [n]                - show last n frames (default 5)
  frame <id>              - show a specific frame by index
  verify                  - verify integrity hashes of all frames
  snapshot                - save a deterministic snapshot of memory
  shell                   - interactive mode
  help                    - show commands
  exit                    - quit CLI
===================================================
"""


# -----------------------------------------------------------
# Integrity Utilities
# -----------------------------------------------------------

def compute_frame_hash(frame: RecapFrame) -> str:
    """
    Deterministic SHA-256 hash of a frame's serialized content.
    Excludes any existing hash field to avoid recursion.
    """
    d = frame.to_dict()
    d.pop("hash", None)
    payload = json.dumps(d, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def verify_integrity() -> bool:
    """
    Verifies all frames in memory for correctness.
    Returns True if clean, False if corruption detected.
    """
    if not os.path.exists(MEMORY_FILE):
        print("[OK] No memory file found — nothing to verify.")
        return True

    frames: List[RecapFrame] = load_all()
    clean = True

    for idx, frame in enumerate(frames):
        stored = getattr(frame, "hash", None)
        computed = compute_frame_hash(frame)

        if stored and stored != computed:
            print(f"[ERROR] Frame {idx} hash mismatch.")
            print(f"        stored:  {stored}")
            print(f"        computed:{computed}")
            clean = False

    if clean:
        print("[OK] All frames verified successfully.")
    return clean


# -----------------------------------------------------------
# CLI UI Helpers
# -----------------------------------------------------------

def _read_block(label: str) -> str:
    print(f"Enter {label} (finish with a single '.' on its own line):")
    lines = []
    while True:
        line = input()
        if line.strip() == ".":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def pretty(obj):
    print(json.dumps(obj, indent=2))


def print_bundle(bundle: ContextBundle):
    print("=== Reconstructed Context ===")
    print(f"Project summary       : {bundle.project_summary}")
    print(f"Active workstream     : {bundle.active_workstream}")
    print(f"Known constraints      : {bundle.known_constraints}")
    print(f"User style             : {bundle.user_prefs.style}")
    print(f"User tone              : {bundle.user_prefs.tone}")
    print(f"User constraints       : {bundle.user_prefs.constraints}")
    print("Recommended next steps:")
    for step in bundle.recommended_next_steps:
        print(f"  - {step}")
    print("")
    print(f"Supporting frames: {len(bundle.supporting_frames)}")
    for i, f in enumerate(bundle.supporting_frames):
        print(f"  [{i}] {f.timestamp} | {', '.join(f.key_topics)}")


# -----------------------------------------------------------
# Snapshot
# -----------------------------------------------------------

def create_snapshot() -> None:
    """
    Save a deterministic snapshot of all frames and their hashes.
    """
    frames = load_all()
    snap = {
        "total_frames": len(frames),
        "frames": [],
    }

    for idx, f in enumerate(frames):
        d = f.to_dict()
        d["hash"] = compute_frame_hash(f)
        snap["frames"].append(d)

    os.makedirs("memory/snapshots", exist_ok=True)
    name = f"memory/snapshots/snapshot_{len(frames)}.json"

    with open(name, "w") as f:
        json.dump(snap, f, indent=2)

    print(f"[OK] Snapshot saved → {name}")


# -----------------------------------------------------------
# Commands
# -----------------------------------------------------------

def cmd_save():
    if not verify_integrity():
        print("[ABORT] Memory is corrupted. Refusing to write new frames.")
        return

    user_msg = _read_block("user message")
    assistant_msg = _read_block("assistant message")

    frame = api.save_context(user_msg, assistant_msg)
    frame_hash = compute_frame_hash(frame)

    print("\nSaved frame:")
    print(f"  timestamp : {frame.timestamp}")
    print(f"  topics    : {', '.join(frame.key_topics)}")
    print(f"  hash      : {frame_hash}")


def cmd_load():
    bundle = api.load_context()
    print_bundle(bundle)


def cmd_search(args: List[str]):
    if not args:
        print("Usage: search <keyword>")
        return
    query = " ".join(args)
    bundle = api.load_context(query=query)
    print_bundle(bundle)


def cmd_tail(n: int = 5):
    frames = load_all()
    if not frames:
        print("[EMPTY] No frames stored.")
        return

    tail = frames[-n:]
    for idx, f in enumerate(tail):
        print(f"\n--- Frame {len(frames) - len(tail) + idx} ---")
        pretty(f.to_dict())


def cmd_frame(idx: int):
    frames = load_all()
    if idx < 0 or idx >= len(frames):
        print(f"[ERROR] Frame index out of range (0–{len(frames)-1})")
        return
    pretty(frames[idx].to_dict())


def cmd_shell():
    print("Entering SCPCE interactive shell. Type 'help' for commands.")
    while True:
        try:
            raw = input("scpce> ").strip()
        except EOFError:
            break

        if not raw:
            continue

        parts = raw.split()
        cmd = parts[1:] if len(parts) > 1 else []
        command = parts[0]

        if command == "exit":
            break
        elif command == "help":
            print(BANNER)
        elif command == "save":
            cmd_save()
        elif command == "load":
            cmd_load()
        elif command == "search":
            cmd_search(cmd)
        elif command == "tail":
            n = int(cmd[0]) if cmd else 5
            cmd_tail(n)
        elif command == "frame":
            if not cmd:
                print("Usage: frame <index>")
            else:
                cmd_frame(int(cmd[0]))
        elif command == "verify":
            verify_integrity()
        elif command == "snapshot":
            create_snapshot()
        else:
            print(f"[ERROR] Unknown command: {command}")


# -----------------------------------------------------------
# Main Entry
# -----------------------------------------------------------

def main(argv: List[str]):
    if len(argv) == 1:
        print(BANNER)
        return

    cmd = argv[1]

    if cmd == "save":
        cmd_save()
    elif cmd == "load":
        cmd_load()
    elif cmd == "search":
        cmd_search(argv[2:])
    elif cmd == "tail":
        n = int(argv[2]) if len(argv) > 2 else 5
        cmd_tail(n)
    elif cmd == "frame":
        if len(argv) < 3:
            print("Usage: frame <index>")
        else:
            cmd_frame(int(argv[2]))
    elif cmd == "verify":
        verify_integrity()
    elif cmd == "snapshot":
        create_snapshot()
    elif cmd == "shell":
        cmd_shell()
    else:
        print(BANNER)


if __name__ == "__main__":
    main(sys.argv)
