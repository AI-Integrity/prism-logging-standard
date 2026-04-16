"""
PRISM Log integrity helper.

Generates tamper-evident SHA-256 hashes for PRISM logs, supporting
the "protection against unauthorised modification" expectation of
logging regulations (e.g., EU AI Act Article 12(3)).

Two modes:

1. Independent hash — each log gets its own hash, stored alongside.
   Useful for per-record integrity checks.

2. Chained hash — each log's hash includes the previous log's hash.
   Creates a tamper-evident chain; altering any past log invalidates
   all subsequent hashes. Analogous to a simple audit trail.

Usage:
    from tools.prism_hash import hash_log, HashChain

    # Independent
    h = hash_log("C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro",
                 timestamp="2026-04-16T10:30:00Z",
                 session_id="s_abc123")

    # Chained
    chain = HashChain()
    h1 = chain.add(log1, ts1, sid1)
    h2 = chain.add(log2, ts2, sid2)
    # Verify later:
    assert chain.verify(records)
"""
import hashlib
import json
from typing import Optional


def hash_log(code: str,
             timestamp: str,
             session_id: str,
             previous_hash: Optional[str] = None) -> str:
    """
    Produce a deterministic SHA-256 hash of a PRISM log record.

    Args:
        code: The PRISM code string, e.g., "C:MD/IXi | V:Ben<Sel | ..."
        timestamp: ISO 8601 timestamp when the log was emitted
        session_id: Identifier of the conversation/session
        previous_hash: For chained hashing, the hash of the previous log
                       in the same audit stream. None for independent hashing.

    Returns:
        A 64-character hex string representing the SHA-256 hash.

    Input is serialized canonically so the same inputs always produce
    the same hash. JSON is used with sort_keys to guarantee byte-identical
    serialization across Python versions.
    """
    payload = {
        "code": code,
        "timestamp": timestamp,
        "session_id": session_id,
    }
    if previous_hash is not None:
        payload["previous_hash"] = previous_hash

    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def verify_log(code: str,
               timestamp: str,
               session_id: str,
               claimed_hash: str,
               previous_hash: Optional[str] = None) -> bool:
    """
    Verify that a claimed hash matches the PRISM log inputs.

    Returns True if the claimed hash matches a freshly computed hash
    over the same inputs. False otherwise.
    """
    expected = hash_log(code, timestamp, session_id, previous_hash)
    return expected == claimed_hash


class HashChain:
    """
    Maintain a chained hash over a sequence of PRISM logs.

    Each new log's hash incorporates the previous log's hash,
    creating a tamper-evident chain. Altering any past log
    invalidates every subsequent hash in the chain.
    """

    def __init__(self, genesis_hash: Optional[str] = None):
        """
        Initialize the chain.

        Args:
            genesis_hash: Optional starting hash, e.g., a hash of your
                          deployment's configuration. If None, the first
                          log has no previous_hash.
        """
        self._last = genesis_hash

    def add(self, code: str, timestamp: str, session_id: str) -> str:
        """
        Add a new log to the chain. Returns its hash.
        """
        h = hash_log(code, timestamp, session_id, previous_hash=self._last)
        self._last = h
        return h

    @property
    def last_hash(self) -> Optional[str]:
        """The most recent hash in the chain, or None if empty."""
        return self._last

    @staticmethod
    def verify(records: list, genesis_hash: Optional[str] = None) -> bool:
        """
        Verify a full chain of records.

        Args:
            records: List of dicts, each with keys:
                     "code", "timestamp", "session_id", "hash"
            genesis_hash: Starting hash expected for the first record.

        Returns:
            True if every record's hash matches recomputation,
            AND each record's previous_hash matches the preceding record's hash.
            False if any record has been modified, removed, or reordered.
        """
        previous = genesis_hash
        for r in records:
            expected = hash_log(
                r["code"], r["timestamp"], r["session_id"],
                previous_hash=previous
            )
            if expected != r["hash"]:
                return False
            previous = r["hash"]
        return True


# ---------------- CLI for quick testing ----------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2 or sys.argv[1] == "--help":
        print(__doc__)
        print("\nQuick CLI:")
        print("  prism_hash.py demo                        # run demo")
        print("  prism_hash.py hash <code> <ts> <sid>      # hash one log")
        sys.exit(0)

    if sys.argv[1] == "demo":
        print("=== Demo: independent hashes ===")
        logs = [
            ("C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro", "2026-04-16T10:30:00Z", "s1"),
            ("C:FN/IRs | V:Ach<Sec | E:Pop<Gui | S:Alt<Pro", "2026-04-16T10:31:15Z", "s1"),
            ("C:TC/GRl | V:Sti<Sec | E:Ane<Cas | S:Alt<Pro", "2026-04-16T10:32:40Z", "s1"),
        ]
        for code, ts, sid in logs:
            h = hash_log(code, ts, sid)
            print(f"  {h[:16]}...  {code[:40]}")

        print("\n=== Demo: chained hashes ===")
        chain = HashChain()
        records = []
        for code, ts, sid in logs:
            h = chain.add(code, ts, sid)
            records.append({"code": code, "timestamp": ts, "session_id": sid, "hash": h})
            print(f"  {h[:16]}...  chained from previous")

        print("\nVerifying intact chain...", "OK" if HashChain.verify(records) else "FAIL")

        # Tamper with a record
        tampered = [dict(r) for r in records]
        tampered[1]["code"] = "C:FN/IRs | V:Sec<Ach | E:Pop<Gui | S:Alt<Pro"  # swapped V order
        print("Verifying tampered chain...", "OK" if HashChain.verify(tampered) else "FAIL (expected)")
        sys.exit(0)

    if sys.argv[1] == "hash" and len(sys.argv) >= 5:
        code, ts, sid = sys.argv[2], sys.argv[3], sys.argv[4]
        print(hash_log(code, ts, sid))
        sys.exit(0)

    print("Unknown command. Run with --help for usage.")
    sys.exit(1)
