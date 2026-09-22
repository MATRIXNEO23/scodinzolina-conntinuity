#!/usr/bin/env python3
"""GPTina long-term RAG memory.

Canonical repository files are READ-ONLY inputs.
This program writes only inside rag/index/.
No external Python dependencies are required.
"""

from __future__ import annotations

import argparse
import contextlib
import fnmatch
import hashlib
import json
import math
import os
import re
import sqlite3
import subprocess
import sys
import time
import uuid
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from memory_schema import (
    build_memory_resolver,
    parse_front_matter,
    validate_durable_v2,
)

ROOT = Path(__file__).resolve().parents[1]
RAG_ROOT = ROOT / "rag"
INDEX_DIR = RAG_ROOT / "index"
GENERATION_ROOT = INDEX_DIR / ".projection-generations"
CURRENT_GENERATION_FILE = INDEX_DIR / ".projection-current"
LEGACY_INDEX_FILE = INDEX_DIR / "memory_chunks.jsonl"
LEGACY_META_FILE = INDEX_DIR / "index_meta.json"
LEGACY_SQLITE_FILE = INDEX_DIR / "gptina_memory.sqlite3"


def _active_projection_paths() -> tuple[Path, Path, Path]:
    """Resolve one complete published generation, or the legacy layout."""
    try:
        generation = CURRENT_GENERATION_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        generation = ""
    if generation and Path(generation).name == generation:
        directory = GENERATION_ROOT / generation
        required = (
            directory / "memory_chunks.jsonl",
            directory / "index_meta.json",
            directory / "gptina_memory.sqlite3",
        )
        if all(path.is_file() for path in required):
            return required
    return LEGACY_INDEX_FILE, LEGACY_META_FILE, LEGACY_SQLITE_FILE


INDEX_FILE, META_FILE, SQLITE_FILE = _active_projection_paths()
EXACT_SQLITE_FILE = INDEX_DIR / "gptina_exact_trigram.sqlite3"
MANIFEST_FILE = RAG_ROOT / "memory_manifest.json"
VISUAL_INDEX_FILE = INDEX_DIR / "GPTINA_VISUAL_CHRONOLOGY.md"
CURRENT_CONTEXT_FILE = INDEX_DIR / "CURRENT_CONTEXT.md"
FAST_RECALL_FILE = INDEX_DIR / "GPTINA_FAST_RECALL.md"
TOKEN_RE = re.compile(r"[0-9A-Za-zÀ-ÖØ-öø-ÿ_]+", re.UNICODE)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
DATE_RE = re.compile(r"(20\d{2})[-_](\d{2})[-_](\d{2})")
COMPACT_DATE_RE = re.compile(r"(20\d{2})(\d{2})(\d{2})")
CHECKPOINT_RE = re.compile(r"checkpoints/(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.md")
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
_DIRTY_PREVIEW_FINGERPRINT: str | None = None
MONTHS_IT = {
    "gennaio": "01", "febbraio": "02", "marzo": "03", "aprile": "04",
    "maggio": "05", "giugno": "06", "luglio": "07", "agosto": "08",
    "settembre": "09", "ottobre": "10", "novembre": "11", "dicembre": "12",
}
def fail(msg: str) -> None:
    raise SystemExit(msg)


def ensure_inside_rag(path: Path) -> None:
    """Hard safety boundary: generated files may live only under rag/."""
    rp = path.resolve()
    rr = RAG_ROOT.resolve()
    if rp != rr and rr not in rp.parents:
        fail(f"Refusing write outside rag/: {path}")


def atomic_write(path: Path, text: str) -> None:
    ensure_inside_rag(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    ensure_inside_rag(tmp)
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def atomic_write_bytes(path: Path, payload: bytes) -> None:
    ensure_inside_rag(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    ensure_inside_rag(tmp)
    tmp.write_bytes(payload)
    tmp.replace(path)


def durable_atomic_write(path: Path, payload: bytes) -> None:
    """Publish one small file durably; used for the generation pointer."""
    ensure_inside_rag(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    ensure_inside_rag(tmp)
    with tmp.open("wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    tmp.replace(path)
    try:
        directory_fd = os.open(path.parent, os.O_RDONLY)
    except (AttributeError, OSError):
        return
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def _set_projection_paths(directory: Path) -> None:
    global INDEX_FILE, META_FILE, SQLITE_FILE
    INDEX_FILE = directory / "memory_chunks.jsonl"
    META_FILE = directory / "index_meta.json"
    SQLITE_FILE = directory / "gptina_memory.sqlite3"


def _refresh_projection_paths() -> None:
    global INDEX_FILE, META_FILE, SQLITE_FILE
    INDEX_FILE, META_FILE, SQLITE_FILE = _active_projection_paths()


@contextlib.contextmanager
def projection_build_lock():
    """Serialize every derived-index publisher in this checkout."""
    lock_file = INDEX_DIR / ".projection-build.lock"
    ensure_inside_rag(lock_file)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    handle = lock_file.open("a+")
    try:
        try:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        except ImportError:  # pragma: no cover - Windows fallback
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        yield
    finally:
        try:
            try:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            except ImportError:  # pragma: no cover - Windows fallback
                import msvcrt
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        finally:
            handle.close()


def load_manifest() -> dict:
    return json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def excluded(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, p) for p in patterns)


def expand_sources(manifest: dict) -> list[tuple[Path, dict]]:
    found: dict[str, tuple[Path, dict]] = {}
    excludes = manifest.get("exclude", [])

    # Canonical sources outside rag/ are immutable inputs.
    for spec in manifest.get("sources", []):
        pattern = spec["pattern"]
        candidates = [ROOT / pattern] if not any(c in pattern for c in "*?[") else ROOT.glob(pattern)
        for p in candidates:
            p = Path(p)
            if not p.is_file():
                continue
            rp = rel(p)
            if rp.startswith("rag/") or excluded(rp, excludes):
                continue
            found[rp] = (p, spec)

    # Owner-scoped RAG sources are explicit in the manifest. This keeps GPTina
    # memories/transcripts searchable without ever ingesting Tessa's memory.
    rag_excludes = manifest.get(
        "rag_exclude",
        ["rag/index/**", "rag/memories/tessa/**"],
    )
    for spec in manifest.get("rag_sources", []):
        pattern = spec["pattern"]
        candidates = [ROOT / pattern] if not any(c in pattern for c in "*?[") else ROOT.glob(pattern)
        for p in candidates:
            p = Path(p)
            if not p.is_file():
                continue
            rp = rel(p)
            if not rp.startswith("rag/") or excluded(rp, rag_excludes):
                continue
            found[rp] = (p, spec)

    # Backward-compatible fallback for older manifests: include GPTina/legacy
    # memories in both Markdown and JSON, but never Tessa-owned memories.
    if not manifest.get("rag_sources"):
        memories = RAG_ROOT / "memories"
        if memories.exists():
            for pattern in ("*.md", "*.json"):
                for p in memories.rglob(pattern):
                    rp = rel(p)
                    if excluded(rp, ["rag/memories/tessa/**", "rag/memories/README.md"]):
                        continue
                    found[rp] = (
                        p,
                        {"pattern": rp, "priority": 1.22, "kind": "rag_memory"},
                    )

    return [found[k] for k in sorted(found)]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def tokenize(text: str) -> list[str]:
    return [m.group(0).casefold() for m in TOKEN_RE.finditer(text)]


def extract_date(path: str) -> str | None:
    m = DATE_RE.search(path)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    compact = COMPACT_DATE_RE.search(path)
    if compact:
        return f"{compact.group(1)}-{compact.group(2)}-{compact.group(3)}"
    return None


def query_date_hint(query: str) -> str | None:
    direct = DATE_RE.search(query)
    if direct:
        return f"{direct.group(1)}-{direct.group(2)}-{direct.group(3)}"

    compact = COMPACT_DATE_RE.search(query)
    if compact:
        return f"{compact.group(1)}-{compact.group(2)}-{compact.group(3)}"

    lower = query.casefold()
    month_names = "|".join(MONTHS_IT)
    natural = re.search(
        rf"\b([0-3]?\d)\s+({month_names})(?:\s+(20\d{{2}}))?\b",
        lower,
    )
    if not natural:
        return None
    day = int(natural.group(1))
    if day < 1 or day > 31:
        return None
    month = MONTHS_IT[natural.group(2)]
    year = natural.group(3)
    return f"{year}-{month}-{day:02d}" if year else f"--{month}-{day:02d}"


def query_profile(query: str) -> tuple[set[str], str | None]:
    lower = query.casefold()
    profile: set[str] = set()
    if any(w in lower for w in ("immagine", "foto", "fotina", "volto", "visual", "media/")):
        profile.add("visual")
    if query_date_hint(query) or any(w in lower for w in ("quando", "prima", "dopo", "quella volta", "cronologia", "data")):
        profile.add("temporal")
    if any(w in lower for w in ("adesso", "ora", "corrente", "stato attuale", "ultimo", "ultima")):
        profile.add("current")
    if '"' in query or any(w in lower for w in ("esattamente", "testo esatto", "parole esatte", "cosa avevi detto", "che parole")):
        profile.add("exact")
    return profile, query_date_hint(query)


def git_blob_sha(path: str) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "-s", "--", path],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    line = proc.stdout.strip()
    if not line:
        return None
    parts = line.split()
    return parts[1] if len(parts) >= 2 else None


def git_worktree_dirty() -> bool:
    try:
        proc = subprocess.run(
            [
                "git", "-C", str(ROOT), "status", "--porcelain",
                "--untracked-files=normal",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return True
    return bool(proc.stdout.strip())


def git_head() -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return proc.stdout.strip() or None


def git_path_exists_at(revision: str, path: str) -> bool:
    try:
        subprocess.run(
            ["git", "-C", str(ROOT), "cat-file", "-e", f"{revision}:{path}"],
            capture_output=True,
            check=True,
        )
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def git_revision_exists(revision: str) -> bool:
    try:
        subprocess.run(
            ["git", "-C", str(ROOT), "cat-file", "-e", f"{revision}^{{commit}}"],
            capture_output=True,
            check=True,
        )
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def current_source_fingerprint(manifest: dict) -> str:
    rows: list[str] = []
    for path, _spec in expand_sources(manifest):
        rp = rel(path)
        rows.append(f"{rp}\0{sha256_text(decode_source(path))}")
    return sha256_text("\n".join(sorted(rows)))


def dirty_preview_fingerprint(manifest: dict, *, refresh: bool = False) -> str:
    """Fingerprint explicitly non-canonical previews without stale reuse."""
    global _DIRTY_PREVIEW_FINGERPRINT
    _DIRTY_PREVIEW_FINGERPRINT = current_source_fingerprint(manifest)
    return _DIRTY_PREVIEW_FINGERPRINT


def supersession_statuses() -> dict[str, tuple[str, str]]:
    """Return target path -> (effective status, replacing path)."""
    memories = RAG_ROOT / "memories" / "gptina"
    if not memories.is_dir():
        return {}
    resolver, metadata, _errors = build_memory_resolver(ROOT, memories)
    path_to_id = {path: memory_id for memory_id, path in resolver.items()}
    edges: dict[str, list[str]] = {}
    for memory_id, meta in metadata.items():
        targets: list[str] = []
        for target in meta.get("supersedes") or []:
            target_id = target if target in resolver else path_to_id.get(str(target))
            if target_id and target_id in resolver:
                targets.append(target_id)
        edges[memory_id] = targets

    # Front matter is append-only: an older record can still literally say
    # status=current even after a later correction supersedes it. Resolve only
    # the effective current roots, i.e. current records that are not reachable
    # from another current record. This makes A <- B <- C resolve to C without
    # rewriting A or B.
    current_ids = {
        memory_id
        for memory_id, meta in metadata.items()
        if str(meta.get("status", "current")) == "current"
    }
    superseded_by_current: set[str] = set()
    for root_id in current_ids:
        pending = list(edges.get(root_id, []))
        seen: set[str] = set()
        while pending:
            target_id = pending.pop()
            if target_id in seen:
                continue
            seen.add(target_id)
            superseded_by_current.add(target_id)
            pending.extend(edges.get(target_id, []))
    active_roots = current_ids - superseded_by_current

    result: dict[str, tuple[str, str]] = {}
    for replacing_id in sorted(active_roots):
        replacing_path = resolver[replacing_id]
        pending = list(edges.get(replacing_id, []))
        seen: set[str] = set()
        while pending:
            target_id = pending.pop()
            if target_id in seen:
                continue
            seen.add(target_id)
            result[resolver[target_id]] = ("superseded", replacing_path)
            pending.extend(edges.get(target_id, []))
    return result


def memory_status(path: str, manifest: dict, content: str) -> tuple[str, str | None]:
    override = manifest.get("status_overrides", {}).get(path)
    if override:
        return str(override.get("status", "current")), override.get("replaced_by")

    if content.startswith("---\n"):
        try:
            meta = parse_front_matter(content)
            status = meta.get("status")
            if status in {"current", "superseded", "invalidated", "historical"}:
                return str(status), None
        except ValueError:
            pass

    opening = content[:900].casefold()
    if path.startswith("rag/memories/") and (
        "# rettifica" in opening
        or "stato:** invalidato" in opening
        or "non deve essere usata come memoria canonica" in opening
    ):
        return "invalidated", None
    return "current", None


def decode_source(path: Path) -> str:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json" and path.as_posix().startswith(str((RAG_ROOT / "memories").as_posix())):
        try:
            obj = json.loads(raw)
            body = obj.get("text") or obj.get("memory") or obj.get("content")
            if body:
                return str(body)
        except json.JSONDecodeError:
            pass
    return raw


def section_blocks(text: str) -> list[tuple[str, str]]:
    """Split Markdown by headings while retaining heading context."""
    lines = text.splitlines()
    blocks: list[tuple[str, list[str]]] = []
    heading = "(root)"
    buf: list[str] = []
    for line in lines:
        m = HEADING_RE.match(line)
        if m:
            if buf:
                blocks.append((heading, buf))
            heading = m.group(2).strip()
            buf = [line]
        else:
            buf.append(line)
    if buf:
        blocks.append((heading, buf))
    return [(h, "\n".join(b).strip()) for h, b in blocks if "\n".join(b).strip()]


def chunk_text(text: str, max_chars: int, overlap: int, min_chars: int) -> list[tuple[str, int, str]]:
    out: list[tuple[str, int, str]] = []
    for heading, block in section_blocks(text):
        if len(block) <= max_chars:
            if len(block) >= min_chars:
                out.append((heading, 0, block))
            continue
        start = 0
        n = 0
        while start < len(block):
            end = min(len(block), start + max_chars)
            if end < len(block):
                cut = block.rfind("\n", start, end)
                if cut <= start + max_chars // 2:
                    cut = block.rfind(". ", start, end)
                    if cut > start:
                        cut += 1
                if cut > start:
                    end = cut
            piece = block[start:end].strip()
            if len(piece) >= min_chars:
                out.append((heading, n, piece))
                n += 1
            if end >= len(block):
                break
            start = max(start + 1, end - overlap)
    return out


def git_history_versions(path: str) -> Iterable[tuple[str, str]]:
    """Yield distinct historical contents for path, read-only via git show."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(ROOT), "log", "--format=%H", "--", path],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return

    seen_hashes: set[str] = set()
    for commit in proc.stdout.splitlines():
        commit = commit.strip()
        if not commit:
            continue
        try:
            show = subprocess.run(
                ["git", "-C", str(ROOT), "show", f"{commit}:{path}"],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError:
            continue
        content = show.stdout
        h = sha256_text(content)
        if h in seen_hashes:
            continue
        seen_hashes.add(h)
        yield commit, content


@dataclass
class SourceVersion:
    path: str
    kind: str
    priority: float
    revision: str
    content: str
    historical: bool
    status: str
    replaced_by: str | None


def collect_versions(include_history: bool) -> list[SourceVersion]:
    manifest = load_manifest()
    effective_supersessions = supersession_statuses()
    versions: list[SourceVersion] = []
    for path, spec in expand_sources(manifest):
        rp = rel(path)
        content = decode_source(path)
        current_hash = sha256_text(content)
        kind = spec.get("kind", "source")
        priority = float(spec.get("priority", 1.0))
        status, replaced_by = memory_status(rp, manifest, content)
        if status == "current" and rp in effective_supersessions:
            status, replaced_by = effective_supersessions[rp]

        if status == "invalidated":
            priority *= 0.30
        elif status == "superseded":
            priority *= 0.60

        versions.append(
            SourceVersion(
                path=rp,
                kind=kind,
                priority=priority,
                revision="WORKTREE",
                content=content,
                historical=False,
                status=status,
                replaced_by=replaced_by,
            )
        )
        if include_history and not rp.startswith("rag/"):
            for commit, old in git_history_versions(rp) or []:
                if sha256_text(old) == current_hash:
                    continue
                versions.append(
                    SourceVersion(
                        path=rp,
                        kind=spec.get("kind", "source"),
                        priority=float(spec.get("priority", 1.0)),
                        revision=commit,
                        content=old,
                        historical=True,
                        status="historical",
                        replaced_by=None,
                    )
                )
    return versions



def sqlite_connect(path: Path | None = None) -> sqlite3.Connection:
    path = path or SQLITE_FILE
    ensure_inside_rag(path)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS source_state (
            source TEXT NOT NULL,
            revision TEXT NOT NULL,
            source_sha256 TEXT NOT NULL,
            kind TEXT NOT NULL,
            priority REAL NOT NULL,
            historical INTEGER NOT NULL,
            status TEXT NOT NULL,
            replaced_by TEXT,
            date_hint TEXT,
            PRIMARY KEY (source, revision)
        );

        CREATE TABLE IF NOT EXISTS index_meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
            chunk_id UNINDEXED,
            source UNINDEXED,
            revision UNINDEXED,
            historical UNINDEXED,
            status UNINDEXED,
            kind UNINDEXED,
            priority UNINDEXED,
            date_hint UNINDEXED,
            heading,
            text,
            tokenize='unicode61 remove_diacritics 2'
        );
        """
    )
    return conn


def sqlite_meta(conn: sqlite3.Connection) -> dict[str, str]:
    return {
        str(row["key"]): str(row["value"])
        for row in conn.execute("SELECT key, value FROM index_meta")
    }


def sqlite_semantically_valid(conn: sqlite3.Connection) -> bool:
    """Validate logical completeness beyond SQLite's physical quick_check."""
    try:
        meta = sqlite_meta(conn)
        if meta.get("build_complete") != "1":
            return False
        expected_sources = int(meta["source_versions"])
        expected_chunks = int(meta["chunks"])
        actual_sources = int(conn.execute("SELECT count(*) FROM source_state").fetchone()[0])
        actual_chunks = int(conn.execute("SELECT count(*) FROM chunks_fts").fetchone()[0])
        orphan_chunks = int(conn.execute(
            """
            SELECT count(*) FROM chunks_fts AS c
            LEFT JOIN source_state AS s
              ON s.source=c.source AND s.revision=c.revision
            WHERE s.source IS NULL
            """
        ).fetchone()[0])
    except (KeyError, ValueError, TypeError, sqlite3.DatabaseError):
        return False
    return (
        expected_sources == actual_sources
        and expected_chunks == actual_chunks
        and orphan_chunks == 0
        and (actual_sources == 0) == (actual_chunks == 0)
    )


def set_sqlite_meta(conn: sqlite3.Connection, values: dict[str, str]) -> None:
    conn.executemany(
        """
        INSERT INTO index_meta(key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """,
        list(values.items()),
    )


def sqlite_index_is_fresh(include_history: bool, allow_dirty_preview: bool = False) -> bool:
    if not SQLITE_FILE.exists():
        return False
    try:
        conn = sqlite_connect()
        meta = sqlite_meta(conn)
        if not sqlite_semantically_valid(conn):
            return False
    except sqlite3.DatabaseError:
        return False
    finally:
        try:
            conn.close()
        except Exception:
            pass

    manifest_hash = sha256_text(MANIFEST_FILE.read_text(encoding="utf-8"))
    if meta.get("include_git_history") != ("1" if include_history else "0"):
        return False
    if meta.get("manifest_sha256") != manifest_hash:
        return False
    if meta.get("build_complete") != "1":
        return False
    head = git_head()
    if not head or meta.get("git_head") != head:
        return False
    dirty = git_worktree_dirty()
    if not dirty:
        return meta.get("snapshot_mode") in {None, "committed"}
    if not allow_dirty_preview or meta.get("snapshot_mode") != "dirty-preview":
        return False
    return meta.get("source_fingerprint") == dirty_preview_fingerprint(load_manifest())


def sync_sqlite_index(
    include_history: bool = False,
    allow_dirty_preview: bool = False,
) -> dict[str, int]:
    return build_all_projections(include_history, allow_dirty_preview)


def _sync_sqlite_index_locked(
    include_history: bool = False,
    allow_dirty_preview: bool = False,
) -> dict[str, int]:
    sync_started = time.perf_counter()
    expected_head = git_head()
    manifest = load_manifest()
    dirty = git_worktree_dirty()
    if dirty and not allow_dirty_preview:
        fail(
            "Refusing canonical SQLite sync from a dirty worktree. "
            "Commit first or use explicit dirty-preview mode."
        )
    cfg = manifest.get("chunking", {})
    max_chars = int(cfg.get("max_chars", 1400))
    overlap = int(cfg.get("overlap_chars", 220))
    min_chars = int(cfg.get("min_chars", 120))
    expected_fingerprint = current_source_fingerprint(manifest)

    discovery_started = time.perf_counter()
    source_versions = collect_versions(include_history)
    discovery_ms = (time.perf_counter() - discovery_started) * 1000.0
    desired: dict[tuple[str, str], SourceVersion] = {
        (sv.path, sv.revision): sv for sv in source_versions
    }

    sqlite_started = time.perf_counter()
    try:
        conn = sqlite_connect()
        conn.execute("PRAGMA quick_check").fetchone()
        if not sqlite_semantically_valid(conn):
            raise sqlite3.DatabaseError("SQLite semantic integrity check failed")
    except sqlite3.DatabaseError:
        try:
            conn.close()
        except Exception:
            pass
        temporary = SQLITE_FILE.with_suffix(SQLITE_FILE.suffix + ".rebuild")
        ensure_inside_rag(temporary)
        for suffix in ("", "-wal", "-shm"):
            candidate = Path(str(temporary) + suffix)
            if candidate.exists():
                candidate.unlink()
        conn = sqlite_connect(temporary)
        rebuild_target = temporary
    else:
        rebuild_target = None
    try:
        current = {
            (str(row["source"]), str(row["revision"])): str(row["source_sha256"])
            for row in conn.execute("SELECT source, revision, source_sha256 FROM source_state")
        }

        removed = set(current) - set(desired)
        changed = {
            key for key, sv in desired.items()
            if current.get(key) != sha256_text(sv.content)
        }

        with conn:
            for source, revision in removed | changed:
                conn.execute(
                    "DELETE FROM chunks_fts WHERE source=? AND revision=?",
                    (source, revision),
                )
                conn.execute(
                    "DELETE FROM source_state WHERE source=? AND revision=?",
                    (source, revision),
                )

            inserted_chunks = 0
            for key in sorted(changed):
                sv = desired[key]
                source_hash = sha256_text(sv.content)
                date_hint = extract_date(sv.path)
                conn.execute(
                    """
                    INSERT INTO source_state(
                        source, revision, source_sha256, kind, priority,
                        historical, status, replaced_by, date_hint
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        sv.path, sv.revision, source_hash, sv.kind, sv.priority,
                        int(sv.historical), sv.status, sv.replaced_by, date_hint,
                    ),
                )
                rows = []
                for heading, ordinal, chunk in chunk_text(
                    sv.content, max_chars, overlap, min_chars
                ):
                    key_text = (
                        f"{sv.path}\0{sv.revision}\0{heading}\0{ordinal}\0{chunk}"
                    )
                    chunk_id = hashlib.sha256(
                        key_text.encode("utf-8")
                    ).hexdigest()[:24]
                    rows.append(
                        (
                            chunk_id, sv.path, sv.revision, int(sv.historical),
                            sv.status, sv.kind, sv.priority, date_hint,
                            heading, chunk,
                        )
                    )
                conn.executemany(
                    """
                    INSERT INTO chunks_fts(
                        chunk_id, source, revision, historical, status, kind,
                        priority, date_hint, heading, text
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    rows,
                )
                inserted_chunks += len(rows)

            set_sqlite_meta(
                conn,
                {
                    "schema_version": "1",
                    "build_complete": "1",
                    "include_git_history": "1" if include_history else "0",
                    "manifest_sha256": sha256_text(
                        MANIFEST_FILE.read_text(encoding="utf-8")
                    ),
                    "git_head": git_head() or "",
                    "snapshot_mode": "dirty-preview" if dirty else "committed",
                    "source_fingerprint": (
                        dirty_preview_fingerprint(manifest, refresh=True)
                        if dirty else current_source_fingerprint(manifest)
                    ),
                    "source_versions": str(len(source_versions)),
                    "chunks": str(sum(
                        1
                        for sv in source_versions
                        for _chunk in chunk_text(sv.content, max_chars, overlap, min_chars)
                    )),
                    "updated_at_epoch": str(int(time.time())),
                },
            )

        if (
            git_head() != expected_head
            or current_source_fingerprint(manifest) != expected_fingerprint
        ):
            raise RuntimeError("Canonical sources changed during SQLite index build; retry.")
        integrity = str(conn.execute("PRAGMA quick_check").fetchone()[0])
        if integrity != "ok":
            raise sqlite3.DatabaseError(f"SQLite quick_check failed: {integrity}")
        if not sqlite_semantically_valid(conn):
            raise sqlite3.DatabaseError("SQLite semantic integrity check failed after build")

        chunks = int(
            conn.execute("SELECT count(*) FROM chunks_fts").fetchone()[0]
        )
        sources = int(
            conn.execute("SELECT count(*) FROM source_state").fetchone()[0]
        )
        result = {
            "sources": sources,
            "chunks": chunks,
            "changed_sources": len(changed),
            "removed_sources": len(removed),
            "inserted_chunks": inserted_chunks,
            "source_discovery_ms": round(discovery_ms, 3),
            "sqlite_update_ms": round((time.perf_counter() - sqlite_started) * 1000.0, 3),
            "total_ms": round((time.perf_counter() - sync_started) * 1000.0, 3),
        }
        if rebuild_target is not None:
            conn.close()
            for suffix in ("-wal", "-shm"):
                Path(str(SQLITE_FILE) + suffix).unlink(missing_ok=True)
            rebuild_target.replace(SQLITE_FILE)
            rebuild_target = None
        return result
    finally:
        conn.close()
        if rebuild_target is not None and rebuild_target.exists():
            rebuild_target.unlink()


def ensure_fresh_sqlite_index(
    include_history: bool = False,
    allow_dirty_preview: bool = False,
) -> None:
    if not sqlite_index_is_fresh(include_history, allow_dirty_preview):
        sync_sqlite_index(
            include_history=include_history,
            allow_dirty_preview=allow_dirty_preview,
        )


def sqlite_search(
    query: str,
    top_k: int,
    include_historical: bool = False,
    include_superseded: bool = False,
    allow_dirty_preview: bool = False,
) -> list[tuple[float, dict]]:
    ensure_fresh_sqlite_index(include_historical, allow_dirty_preview)
    terms = tokenize(query)
    if not terms:
        return []

    # FTS5 candidate generation stays deliberately broad. Routing/status/date
    # logic is applied transparently in Python after candidate selection.
    match = " OR ".join(f'"{term.replace(chr(34), chr(34) * 2)}"' for term in terms)
    profile, requested_date = query_profile(query)
    candidate_limit = max(80, top_k * 20)

    conn = sqlite_connect()
    try:
        rows = conn.execute(
            """
            SELECT
                chunk_id, source, revision, historical, status, kind,
                priority, date_hint, heading, text,
                bm25(chunks_fts, 0,0,0,0,0,0,0,0,2.0,1.0) AS fts_rank
            FROM chunks_fts
            WHERE chunks_fts MATCH ?
            ORDER BY fts_rank
            LIMIT ?
            """,
            (match, candidate_limit),
        ).fetchall()
    finally:
        conn.close()

    query_phrase = " ".join(terms)
    scored: list[tuple[float, dict]] = []
    for row in rows:
        d = dict(row)
        historical = bool(int(d.get("historical") or 0))
        status = str(d.get("status") or "current")
        if not include_historical and historical:
            continue
        if not include_superseded and status in {"superseded", "invalidated"}:
            continue

        # FTS5 bm25 is lower-is-better (normally negative). Convert it into a
        # positive score before applying explicit metadata boosts.
        lexical_score = max(1e-9, -float(d.pop("fts_rank")))
        factors: list[tuple[str, float]] = []
        priority = float(d.get("priority") or 1.0)
        score = lexical_score * priority
        factors.append(("source_priority", priority))
        if historical:
            score *= 0.94
            factors.append(("historical", 0.94))

        searchable = " ".join(
            tokenize(
                str(d.get("text", "")) + " "
                + str(d.get("heading", "")) + " "
                + str(d.get("source", ""))
            )
        )
        if len(terms) > 1 and query_phrase in searchable:
            score *= 1.16
            factors.append(("exact_phrase", 1.16))

        kind = str(d.get("kind") or "")
        if "visual" in profile and kind in {"visual_router", "visual_context", "visual_record"}:
            score *= 1.35
            factors.append(("visual_route", 1.35))
        if "temporal" in profile and kind in {
            "chronology_router", "checkpoint", "micro_checkpoint",
            "gptina_transcript", "raw_session", "chronicle"
        }:
            score *= 1.22
            factors.append(("temporal_route", 1.22))
        if "current" in profile:
            if kind in {"live_context", "micro_checkpoint"}:
                score *= 1.35
                factors.append(("current_live", 1.35))
            elif kind in {"current_router", "gptina_memory", "checkpoint"}:
                score *= 1.20
                factors.append(("current_state", 1.20))
            if kind in {
                "historical_snapshot", "historical_structured_state",
                "historical_live_thread"
            }:
                score *= 0.70
                factors.append(("current_historical_penalty", 0.70))
        if "exact" in profile and kind in {"gptina_transcript", "raw_session"}:
            score *= 1.25
            factors.append(("exact_source", 1.25))

        if requested_date:
            date_hint = d.get("date_hint")
            if requested_date.startswith("--"):
                if date_hint and str(date_hint).endswith(requested_date[1:]):
                    score *= 1.35
                    factors.append(("date_match", 1.35))
            elif date_hint == requested_date:
                score *= 1.35
                factors.append(("date_match", 1.35))

        d["historical"] = historical
        d["score_components"] = {
            "lexical_bm25": lexical_score,
            "factors": factors,
            "final": score,
        }
        scored.append((score, d))

    scored.sort(key=lambda item: item[0], reverse=True)
    diversified: list[tuple[float, dict]] = []
    per_source: Counter[str] = Counter()
    for item in scored:
        source = str(item[1].get("source", ""))
        if per_source[source] >= 2:
            continue
        diversified.append(item)
        per_source[source] += 1
        if len(diversified) >= top_k:
            break
    return diversified


def sqlite_stats(allow_dirty_preview: bool = False) -> dict[str, object]:
    ensure_fresh_sqlite_index(False, allow_dirty_preview)
    conn = sqlite_connect()
    try:
        meta = sqlite_meta(conn)
        return {
            "database": rel(SQLITE_FILE),
            "sources": int(conn.execute("SELECT count(*) FROM source_state").fetchone()[0]),
            "chunks": int(conn.execute("SELECT count(*) FROM chunks_fts").fetchone()[0]),
            "current": int(conn.execute(
                "SELECT count(*) FROM source_state WHERE status='current'"
            ).fetchone()[0]),
            "superseded": int(conn.execute(
                "SELECT count(*) FROM source_state WHERE status='superseded'"
            ).fetchone()[0]),
            "invalidated": int(conn.execute(
                "SELECT count(*) FROM source_state WHERE status='invalidated'"
            ).fetchone()[0]),
            "git_head": meta.get("git_head"),
            "manifest_sha256": meta.get("manifest_sha256"),
            "snapshot_mode": meta.get("snapshot_mode", "legacy"),
        }
    finally:
        conn.close()



def build(
    include_history: bool = False,
    allow_dirty_preview: bool = False,
) -> None:
    build_all_projections(include_history, allow_dirty_preview)


def _build_locked(
    include_history: bool = False,
    allow_dirty_preview: bool = False,
) -> None:
    expected_head = git_head()
    manifest = load_manifest()
    dirty = git_worktree_dirty()
    if dirty and not allow_dirty_preview:
        fail(
            "Refusing canonical JSONL build from a dirty worktree. "
            "Commit first or use explicit dirty-preview mode."
        )
    cfg = manifest.get("chunking", {})
    max_chars = int(cfg.get("max_chars", 1400))
    overlap = int(cfg.get("overlap_chars", 220))
    min_chars = int(cfg.get("min_chars", 120))
    expected_fingerprint = current_source_fingerprint(manifest)

    records: list[dict] = []
    seen_chunk_ids: set[str] = set()
    source_versions = collect_versions(include_history)

    for sv in source_versions:
        source_hash = sha256_text(sv.content)
        for heading, ordinal, chunk in chunk_text(sv.content, max_chars, overlap, min_chars):
            key = f"{sv.path}\0{sv.revision}\0{heading}\0{ordinal}\0{chunk}"
            chunk_id = hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
            if chunk_id in seen_chunk_ids:
                continue
            seen_chunk_ids.add(chunk_id)
            records.append(
                {
                    "id": chunk_id,
                    "source": sv.path,
                    "source_sha256": source_hash,
                    "revision": sv.revision,
                    "historical": sv.historical,
                    "status": sv.status,
                    "replaced_by": sv.replaced_by,
                    "kind": sv.kind,
                    "priority": sv.priority,
                    "date_hint": extract_date(sv.path),
                    "heading": heading,
                    "ordinal": ordinal,
                    "text": chunk,
                }
            )

    payload = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)
    if (
        git_head() != expected_head
        or current_source_fingerprint(manifest) != expected_fingerprint
    ):
        raise RuntimeError("Canonical sources changed during JSONL index build; retry.")
    atomic_write(INDEX_FILE, payload)
    atomic_write(
        META_FILE,
        json.dumps(
            {
                "version": 2,
                "chunks": len(records),
                "source_versions": len(source_versions),
                "include_git_history": include_history,
                "manifest_sha256": sha256_text(MANIFEST_FILE.read_text(encoding="utf-8")),
                "source_fingerprint": current_source_fingerprint(manifest),
                "git_head": git_head(),
                "snapshot_mode": "dirty-preview" if dirty else "committed",
                "canonical_sources_modified": False,
                "write_boundary": "rag/ only",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )
    print(f"Built {len(records)} chunks from {len(source_versions)} source versions -> {INDEX_FILE.relative_to(ROOT)}")


def index_is_fresh(include_history: bool) -> bool:
    if not INDEX_FILE.exists() or not META_FILE.exists():
        return False
    try:
        meta = json.loads(META_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False

    manifest = load_manifest()
    manifest_hash = sha256_text(MANIFEST_FILE.read_text(encoding="utf-8"))
    if bool(meta.get("include_git_history")) != include_history:
        return False
    if meta.get("manifest_sha256") != manifest_hash:
        return False

    dirty = git_worktree_dirty()
    if dirty:
        return (
            meta.get("snapshot_mode") == "dirty-preview"
            and meta.get("source_fingerprint") == current_source_fingerprint(manifest)
        )
    if meta.get("snapshot_mode") not in {None, "committed"}:
        return False

    # Fast path for long-lived repositories: if the checkout HEAD did not
    # change, do not hash/read the whole memory corpus just to answer a query.
    head = git_head()
    if head and meta.get("git_head") == head:
        return True

    # HEAD changed (or git is unavailable): verify content once. If sources are
    # unchanged, advance only the derived index metadata; otherwise rebuild.
    fingerprint = current_source_fingerprint(manifest)
    if meta.get("source_fingerprint") != fingerprint:
        return False

    if head and meta.get("git_head") != head:
        meta["git_head"] = head
        atomic_write(META_FILE, json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    return True


def ensure_fresh_index(include_history: bool) -> None:
    if not index_is_fresh(include_history):
        build(include_history=include_history)


def build_all_projections(
    include_history: bool = False,
    allow_dirty_preview: bool = False,
) -> dict[str, int]:
    """Build a complete immutable generation, then atomically select it."""
    with projection_build_lock():
        _refresh_projection_paths()
        dirty = git_worktree_dirty()
        if dirty and not allow_dirty_preview:
            fail(
                "Refusing projection build from a dirty worktree. "
                "Commit first or use explicit dirty-preview mode."
            )
        expected_head = git_head()
        manifest = load_manifest()
        expected_fingerprint = current_source_fingerprint(manifest)
        previous_paths = (INDEX_FILE, META_FILE, SQLITE_FILE)
        generation = f"gen-{int(time.time() * 1000)}-{uuid.uuid4().hex[:12]}"
        staging = GENERATION_ROOT / (generation + ".staging")
        published = GENERATION_ROOT / generation
        ensure_inside_rag(staging)
        ensure_inside_rag(published)
        staging.mkdir(parents=True, exist_ok=False)
        if previous_paths[2].exists():
            try:
                source_db = sqlite3.connect(
                    f"file:{previous_paths[2]}?mode=ro", uri=True, timeout=30.0
                )
                staged_db = sqlite3.connect(staging / "gptina_memory.sqlite3")
                try:
                    source_db.backup(staged_db)
                finally:
                    staged_db.close()
                    source_db.close()
            except sqlite3.DatabaseError:
                (staging / "gptina_memory.sqlite3").write_bytes(
                    previous_paths[2].read_bytes()
                )
        _set_projection_paths(staging)
        try:
            _build_locked(include_history, allow_dirty_preview)
            stats = _sync_sqlite_index_locked(include_history, allow_dirty_preview)
            json_meta = json.loads(META_FILE.read_text(encoding="utf-8"))
            json_meta["projection_generation"] = generation
            atomic_write(
                META_FILE,
                json.dumps(json_meta, ensure_ascii=False, indent=2) + "\n",
            )
            with sqlite3.connect(SQLITE_FILE) as generation_db:
                set_sqlite_meta(
                    generation_db,
                    {"projection_generation": generation},
                )
            if (
                git_head() != expected_head
                or current_source_fingerprint(manifest) != expected_fingerprint
            ):
                raise RuntimeError("Canonical sources changed during projection transaction; retry.")
            for required in (INDEX_FILE, META_FILE, SQLITE_FILE):
                if not required.is_file():
                    raise RuntimeError(f"Incomplete projection generation: {required.name}")
            with sqlite3.connect(SQLITE_FILE) as validation:
                validation.row_factory = sqlite3.Row
                if validation.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                    raise sqlite3.DatabaseError("Staged SQLite quick_check failed")
                if not sqlite_semantically_valid(validation):
                    raise sqlite3.DatabaseError("Staged SQLite semantic check failed")
                if sqlite_meta(validation).get("projection_generation") != generation:
                    raise sqlite3.DatabaseError("Staged SQLite generation marker mismatch")
            if os.environ.get("GPTINA_TEST_HARD_EXIT_BEFORE_PUBLISH") == "1":
                os._exit(91)
            staging.replace(published)
            durable_atomic_write(CURRENT_GENERATION_FILE, (generation + "\n").encode("utf-8"))
            _set_projection_paths(published)
            if os.environ.get("GPTINA_TEST_HARD_EXIT_AFTER_PUBLISH") == "1":
                os._exit(92)
            return stats
        except BaseException:
            _set_projection_paths(previous_paths[0].parent)
            raise
        finally:
            if staging.exists():
                for candidate in staging.iterdir():
                    candidate.unlink(missing_ok=True)
                staging.rmdir()


def load_records() -> list[dict]:
    out = []
    for line in INDEX_FILE.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def bm25_search(
    query: str,
    top_k: int,
    include_historical: bool = False,
    include_superseded: bool = False,
) -> list[tuple[float, dict]]:
    docs = load_records()
    if not include_historical:
        docs = [d for d in docs if not d.get("historical")]
    if not include_superseded:
        docs = [d for d in docs if d.get("status", "current") not in {"superseded", "invalidated"}]
    q = tokenize(query)
    if not q:
        return []
    profile, requested_date = query_profile(query)
    tokenized = [
        tokenize(d["text"] + " " + d.get("heading", "") + " " + d.get("source", ""))
        for d in docs
    ]
    n_docs = len(docs)
    avgdl = sum(map(len, tokenized)) / max(n_docs, 1)
    dfs: Counter[str] = Counter()
    for toks in tokenized:
        for term in set(toks):
            dfs[term] += 1

    k1, b = 1.5, 0.75
    scored: list[tuple[float, dict]] = []
    for d, toks in zip(docs, tokenized):
        tf = Counter(toks)
        dl = len(toks)
        score = 0.0
        for term in q:
            f = tf.get(term, 0)
            if not f:
                continue
            df = dfs.get(term, 0)
            idf = math.log(1.0 + (n_docs - df + 0.5) / (df + 0.5))
            score += idf * (f * (k1 + 1)) / (f + k1 * (1 - b + b * dl / max(avgdl, 1)))
        if score <= 0:
            continue
        score *= float(d.get("priority", 1.0))
        if d.get("historical"):
            score *= 0.94
        heading = d.get("heading", "").casefold()
        if any(term in heading for term in q):
            score *= 1.08

        # Small phrase boost helps local expressions ("la cura", "passo a due",
        # "tu + gptina = casa") beat generic documents containing the words
        # independently, while BM25 still does the main ranking.
        query_phrase = " ".join(q)
        searchable = " ".join(
            tokenize(d["text"] + " " + d.get("heading", "") + " " + d.get("source", ""))
        )
        if len(q) > 1 and query_phrase in searchable:
            score *= 1.16

        kind = d.get("kind", "")
        if "visual" in profile and kind in {"visual_router", "visual_context"}:
            score *= 1.35
        if "temporal" in profile and kind in {
            "chronology_router", "checkpoint", "gptina_transcript", "raw_session", "chronicle"
        }:
            score *= 1.22
        if "current" in profile:
            if kind in {"current_router", "gptina_memory", "checkpoint"}:
                score *= 1.20
            if kind in {"historical_snapshot", "historical_structured_state", "historical_live_thread"}:
                score *= 0.70
        if "exact" in profile and kind in {"gptina_transcript", "raw_session"}:
            score *= 1.25

        if requested_date:
            date_hint = d.get("date_hint")
            if requested_date.startswith("--"):
                if date_hint and date_hint.endswith(requested_date[1:]):
                    score *= 1.35
            elif date_hint == requested_date:
                score *= 1.35

        scored.append((score, d))
    scored.sort(key=lambda x: x[0], reverse=True)

    # Diversify results so one long source or many revisions do not crowd out
    # independent evidence. At most two chunks from the same source.
    diversified: list[tuple[float, dict]] = []
    per_source: Counter[str] = Counter()
    for item in scored:
        source = item[1].get("source", "")
        if per_source[source] >= 2:
            continue
        diversified.append(item)
        per_source[source] += 1
        if len(diversified) >= top_k:
            break
    return diversified


def exact_matches(
    needle: str,
    include_superseded: bool = False,
    limit: int = 20,
    backend: str = "scan",
) -> list[dict]:
    if backend == "trigram":
        return exact_matches_trigram(needle, include_superseded, limit)
    if backend != "scan":
        raise ValueError(f"unknown exact backend: {backend}")
    target = needle.casefold()
    if not target:
        return []

    manifest = load_manifest()
    effective_supersessions = supersession_statuses()
    hits: list[dict] = []
    for path, spec in expand_sources(manifest):
        rp = rel(path)
        content = decode_source(path)
        status, replaced_by = memory_status(rp, manifest, content)
        if status == "current" and rp in effective_supersessions:
            status, replaced_by = effective_supersessions[rp]
        if not include_superseded and status in {"superseded", "invalidated"}:
            continue

        folded = content.casefold()
        start = 0
        while len(hits) < limit:
            pos = folded.find(target, start)
            if pos < 0:
                break
            line_no = content.count("\n", 0, pos) + 1
            lines = content.splitlines()
            lo = max(0, line_no - 2)
            hi = min(len(lines), line_no + 1)
            hits.append(
                {
                    "source": rp,
                    "kind": spec.get("kind", "source"),
                    "status": status,
                    "replaced_by": replaced_by,
                    "date_hint": extract_date(rp),
                    "line": line_no,
                    "snippet": "\n".join(lines[lo:hi]),
                }
            )
            start = pos + max(1, len(needle))
        if len(hits) >= limit:
            break
    return hits


def build_exact_trigram_index() -> dict[str, int | float]:
    """Build an optional, disposable substring index without changing defaults."""
    with projection_build_lock():
        return _build_exact_trigram_index_locked()


def _build_exact_trigram_index_locked() -> dict[str, int | float]:
    if git_worktree_dirty():
        fail("Refusing exact-index build from a dirty worktree; commit first.")
    ensure_inside_rag(EXACT_SQLITE_FILE)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    temporary = EXACT_SQLITE_FILE.with_name(
        EXACT_SQLITE_FILE.name + f".tmp-{os.getpid()}-{uuid.uuid4().hex[:12]}"
    )
    ensure_inside_rag(temporary)

    started = time.perf_counter()
    expected_head = git_head()
    manifest = load_manifest()
    expected_fingerprint = current_source_fingerprint(manifest)
    sources = collect_versions(False)
    conn = sqlite3.connect(temporary)
    try:
        conn.execute("PRAGMA journal_mode=DELETE")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("CREATE TABLE exact_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        conn.execute(
            "CREATE VIRTUAL TABLE exact_fts USING fts5("
            "source UNINDEXED, kind UNINDEXED, status UNINDEXED, "
            "replaced_by UNINDEXED, date_hint UNINDEXED, text, "
            "tokenize='trigram case_sensitive 0')"
        )
        with conn:
            conn.executemany(
                "INSERT INTO exact_fts(source, kind, status, replaced_by, date_hint, text) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    (
                        source.path, source.kind, source.status, source.replaced_by,
                        extract_date(source.path), source.content,
                    )
                    for source in sources
                ),
            )
            conn.executemany(
                "INSERT INTO exact_meta(key, value) VALUES (?, ?)",
                (
                    ("schema_version", "1"),
                    ("build_complete", "1"),
                    ("git_head", git_head() or ""),
                    ("manifest_sha256", sha256_text(MANIFEST_FILE.read_text(encoding="utf-8"))),
                    ("source_fingerprint", current_source_fingerprint(manifest)),
                    ("sources", str(len(sources))),
                ),
            )
    finally:
        conn.close()
    if (
        git_head() != expected_head
        or current_source_fingerprint(manifest) != expected_fingerprint
    ):
        temporary.unlink(missing_ok=True)
        raise RuntimeError("Canonical sources changed during exact-index build; retry.")
    check = sqlite3.connect(temporary)
    try:
        integrity = str(check.execute("PRAGMA quick_check").fetchone()[0])
    finally:
        check.close()
    if integrity != "ok":
        temporary.unlink(missing_ok=True)
        raise sqlite3.DatabaseError(f"Exact SQLite quick_check failed: {integrity}")
    temporary.replace(EXACT_SQLITE_FILE)
    return {
        "sources": len(sources),
        "database_bytes": EXACT_SQLITE_FILE.stat().st_size,
        "build_ms": round((time.perf_counter() - started) * 1000.0, 3),
    }


def exact_trigram_is_fresh() -> bool:
    if not EXACT_SQLITE_FILE.exists() or git_worktree_dirty():
        return False
    try:
        conn = sqlite3.connect(EXACT_SQLITE_FILE)
        meta = dict(conn.execute("SELECT key, value FROM exact_meta"))
    except sqlite3.DatabaseError:
        return False
    finally:
        try:
            conn.close()
        except Exception:
            pass
    return (
        meta.get("schema_version") == "1"
        and meta.get("build_complete") == "1"
        and meta.get("git_head") == (git_head() or "")
        and meta.get("manifest_sha256")
        == sha256_text(MANIFEST_FILE.read_text(encoding="utf-8"))
    )


def exact_matches_trigram(
    needle: str,
    include_superseded: bool = False,
    limit: int = 20,
) -> list[dict]:
    target = needle.casefold()
    if not target:
        return []
    if len(target) < 3:
        return exact_matches(needle, include_superseded, limit, backend="scan")
    if not exact_trigram_is_fresh():
        return exact_matches(needle, include_superseded, limit, backend="scan")

    phrase = '"' + needle.replace('"', '""') + '"'
    conn = sqlite3.connect(EXACT_SQLITE_FILE)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT source, kind, status, replaced_by, date_hint, text "
            "FROM exact_fts WHERE exact_fts MATCH ? LIMIT ?",
            (phrase, max(80, limit * 10)),
        ).fetchall()
    finally:
        conn.close()

    hits: list[dict] = []
    for row in rows:
        status = str(row["status"] or "current")
        if not include_superseded and status in {"superseded", "invalidated"}:
            continue
        content = str(row["text"])
        folded = content.casefold()
        start = 0
        while len(hits) < limit:
            pos = folded.find(target, start)
            if pos < 0:
                break
            line_no = content.count("\n", 0, pos) + 1
            lines = content.splitlines()
            hits.append(
                {
                    "source": str(row["source"]),
                    "kind": str(row["kind"]),
                    "status": status,
                    "replaced_by": row["replaced_by"],
                    "date_hint": row["date_hint"],
                    "line": line_no,
                    "snippet": "\n".join(lines[max(0, line_no - 2):min(len(lines), line_no + 1)]),
                }
            )
            start = pos + max(1, len(needle))
        if len(hits) >= limit:
            break
    return hits


def find_exact(needle: str, include_superseded: bool, limit: int, backend: str) -> None:
    hits = exact_matches(
        needle,
        include_superseded=include_superseded,
        limit=limit,
        backend=backend,
    )
    if not hits:
        print("No exact match.")
        return
    for rank, hit in enumerate(hits, 1):
        print(
            f"\n[{rank}] source={hit['source']} line={hit['line']} "
            f"status={hit['status']} date={hit.get('date_hint')}"
        )
        print(hit["snippet"])


def search(
    query: str,
    top_k: int,
    include_history: bool = False,
    include_superseded: bool = False,
) -> None:
    ensure_fresh_index(include_history)
    results = bm25_search(
        query,
        top_k,
        include_historical=include_history,
        include_superseded=include_superseded,
    )
    if not results:
        print("No matching memories.")
        return
    for rank, (score, d) in enumerate(results, 1):
        print(f"\n[{rank}] score={score:.3f} id={d['id']}")
        print(
            f"source={d['source']} revision={d['revision']} "
            f"historical={d['historical']} status={d.get('status', 'current')}"
        )
        print(f"section={d.get('heading')} sha256={d['source_sha256'][:16]}…")
        print(d["text"].strip())


def create_image_link(
    image_path: str,
    event_at: str,
    status: str,
    event_id: str,
    thread_ids: list[str],
    context_refs: list[str],
    memory_refs: list[str],
    cues: list[str],
) -> Path:
    allowed_status = {
        "archived", "context_incomplete",
        "documented_anchor", "recognized_visual_anchor",
    }
    if status not in allowed_status:
        fail(f"Invalid visual status: {status}")
    if not context_refs or not memory_refs:
        fail("Image links require at least one context ref and one memory ref.")

    image = (ROOT / image_path).resolve()
    media_root = (ROOT / "media").resolve()
    if media_root not in image.parents or not image.is_file():
        fail(f"Image must exist under media/: {image_path}")

    for ref in context_refs + memory_refs:
        if not (ROOT / ref).exists():
            fail(f"Referenced context/memory does not exist: {ref}")

    m = re.match(r"^(20\d{2})-(\d{2})", event_at)
    if not m:
        fail("event_at must begin with YYYY-MM")
    year, month = m.group(1), m.group(2)

    stem = re.sub(r"[^0-9A-Za-zÀ-ÖØ-öø-ÿ_-]+", "-", image.stem).strip("-").casefold()
    target = RAG_ROOT / "media-links" / year / month / f"{stem}.json"
    ensure_inside_rag(target)
    if target.exists():
        fail(f"Image-link record already exists: {rel(target)}")

    blob_sha = git_blob_sha(image_path)
    if not blob_sha:
        raw = image.read_bytes()
        blob_sha = hashlib.sha1(
            f"blob {len(raw)}\0".encode("utf-8") + raw
        ).hexdigest()

    record = {
        "schema_version": 1,
        "owner": "gptina",
        "image_id": "gptina-image-" + hashlib.sha256(
            image_path.encode("utf-8")
        ).hexdigest()[:16],
        "image_path": image_path,
        "blob_sha": blob_sha,
        "bytes": image.stat().st_size,
        "event_at": event_at,
        "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "event_id": event_id,
        "thread_ids": thread_ids,
        "status": status,
        "context_refs": context_refs,
        "memory_refs": memory_refs,
        "cue": cues,
    }
    atomic_write(
        target,
        json.dumps(record, ensure_ascii=False, indent=2) + "\n",
    )
    return target


def verify_future_memory_schema(manifest: dict) -> None:
    cutoff = str(manifest.get("policy", {}).get("memory_schema_required_from", "")).strip()
    if not cutoff:
        return

    memories = RAG_ROOT / "memories" / "gptina"
    if not memories.is_dir():
        return

    resolver, metadata, errors = build_memory_resolver(ROOT, memories)
    baseline = str(
        manifest.get("policy", {}).get("strict_memory_schema_baseline_commit", "")
    ).strip()
    if baseline and not git_revision_exists(baseline):
        fail(
            "Strict-schema baseline commit is unavailable locally: "
            f"{baseline}. Fetch it before verification (a shallow clone may omit it)."
        )
    for path in sorted(memories.rglob("*.md")):
        rp = rel(path)
        date_hint = extract_date(rp)
        if not date_hint or date_hint < cutoff:
            continue
        raw = path.read_text(encoding="utf-8")
        try:
            meta = parse_front_matter(raw)
        except ValueError as exc:
            errors.append(f"{rp}: {exc}")
            continue
        # Existing records at the recorded baseline remain historical inputs.
        # New paths are subject to the strict typed schema without rewriting
        # any pre-existing memory merely for uniformity.
        if not baseline or not git_path_exists_at(baseline, rp):
            errors.extend(f"{rp}: {error}" for error in validate_durable_v2(meta, ROOT))

    # The resolver is derived from canonical Markdown records. Its cardinality
    # is checked here so it can never become an independent source of truth.
    if len(resolver) != len(metadata):
        errors.append("memory resolver cardinality mismatch")

    # Validate supersession as an owner-scoped, acyclic logical graph. Values
    # may be stable memory IDs or legacy canonical paths.
    path_to_id = {path: memory_id for memory_id, path in resolver.items()}
    edges: dict[str, list[str]] = {}
    for memory_id, meta in metadata.items():
        targets: list[str] = []
        for target in meta.get("supersedes") or []:
            resolved_id = target if target in resolver else path_to_id.get(str(target))
            if not resolved_id:
                errors.append(f"{resolver[memory_id]}: supersedes target not found: {target}")
                continue
            targets.append(resolved_id)
        edges[memory_id] = targets
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(memory_id: str) -> None:
        if memory_id in visiting:
            errors.append(f"supersession cycle detected at {memory_id}")
            return
        if memory_id in visited:
            return
        visiting.add(memory_id)
        for target in edges.get(memory_id, []):
            visit(target)
        visiting.remove(memory_id)
        visited.add(memory_id)
    for memory_id in edges:
        visit(memory_id)
    # Because memory files are append-only, a superseded predecessor may still
    # carry status=current in its immutable front matter. Treat only effective
    # roots as current: a current record reached from a later current record is
    # already superseded. Independent active branches that reach the same
    # ancestor remain an error.
    current_ids = {
        memory_id
        for memory_id, meta in metadata.items()
        if str(meta.get("status", "current")) == "current"
    }
    superseded_by_current: set[str] = set()
    for root_id in current_ids:
        pending = list(edges.get(root_id, []))
        seen: set[str] = set()
        while pending:
            target_id = pending.pop()
            if target_id in seen:
                continue
            seen.add(target_id)
            superseded_by_current.add(target_id)
            pending.extend(edges.get(target_id, []))
    active_roots = current_ids - superseded_by_current

    roots_by_target: dict[str, set[str]] = {}
    for root_id in active_roots:
        pending = list(edges.get(root_id, []))
        seen: set[str] = set()
        while pending:
            target_id = pending.pop()
            if target_id in seen:
                continue
            seen.add(target_id)
            roots_by_target.setdefault(target_id, set()).add(root_id)
            pending.extend(edges.get(target_id, []))
    for target_id, roots in roots_by_target.items():
        if len(roots) > 1:
            errors.append(
                f"{resolver[target_id]}: ambiguous current superseders: "
                + ", ".join(sorted(roots))
            )
    if errors:
        fail("Future memory schema violations:\n- " + "\n- ".join(errors))


def verify_boundary() -> None:
    """Verify ownership, index boundaries, image coverage and recovery pointers."""
    manifest = load_manifest()
    policy = manifest.get("policy", {})
    ok = bool(policy.get("canonical_sources_are_immutable_inputs")) and not bool(policy.get("destructive_compaction"))
    if not ok:
        fail("Manifest violates immutable-source policy.")
    for required_policy in (
        "deep_verification_after_every_memory_change",
        "historical_memories_must_remain_recoverable",
        "supersession_is_non_destructive",
    ):
        if policy.get(required_policy) is not True:
            fail(f"Manifest missing canonical memory policy: {required_policy}")

    for p in (INDEX_FILE, META_FILE, SQLITE_FILE):
        ensure_inside_rag(p)

    try:
        probe = sqlite3.connect(":memory:")
        probe.execute("CREATE VIRTUAL TABLE fts5_probe USING fts5(text)")
        probe.close()
    except sqlite3.DatabaseError as exc:
        fail(f"SQLite FTS5 unavailable: {exc}")

    verify_future_memory_schema(manifest)

    try:
        from live_context import verify_live_context
        verify_live_context()
    except ImportError as exc:
        fail(f"Cannot load live-context verifier: {exc}")

    sources = expand_sources(manifest)
    forbidden = [rel(p) for p, _ in sources if rel(p).startswith("rag/memories/tessa/")]
    if forbidden:
        fail(f"Tessa-owned memories entered GPTina index: {forbidden}")

    for path, meta in manifest.get("status_overrides", {}).items():
        src = ROOT / path
        if not src.is_file():
            fail(f"Status override points to missing memory: {path}")
        replacement = meta.get("replaced_by")
        if replacement and not (ROOT / replacement).is_file():
            fail(f"Status override replacement missing: {replacement}")

    if VISUAL_INDEX_FILE.is_file():
        visual = VISUAL_INDEX_FILE.read_text(encoding="utf-8")
        media_dir = ROOT / "media"
        images = [
            p for p in media_dir.rglob("*")
            if p.is_file() and p.suffix.casefold() in IMAGE_SUFFIXES
        ] if media_dir.is_dir() else []
        missing = [p.name for p in images if p.name not in visual]
        if missing:
            fail(f"Images missing from visual chronology: {missing}")

        link_dir = RAG_ROOT / "media-links"
        link_records: dict[str, Path] = {}
        covered_images: set[str] = set()
        if link_dir.is_dir():
            for record_path in link_dir.rglob("*.json"):
                try:
                    record = json.loads(record_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError as exc:
                    fail(f"Invalid image-link JSON {rel(record_path)}: {exc}")
                image_path = str(record.get("image_path") or "")
                if not image_path:
                    fail(f"Image-link record missing image_path: {rel(record_path)}")
                if record.get("owner") != "gptina":
                    fail(f"Image-link owner must be gptina: {rel(record_path)}")

                image_file = ROOT / image_path
                if not image_file.is_file():
                    fail(
                        f"Image-link points to missing media file: "
                        f"{rel(record_path)} -> {image_path}"
                    )

                actual_size = image_file.stat().st_size
                expected_bytes = record.get("bytes")
                if expected_bytes is None or int(expected_bytes) != actual_size:
                    fail(
                        f"Image-link byte size mismatch: {rel(record_path)} "
                        f"expected={expected_bytes} actual={actual_size}"
                    )

                expected_blob = str(record.get("blob_sha") or "")
                actual_blob = git_blob_sha(image_path)
                if not actual_blob:
                    raw_bytes = image_file.read_bytes()
                    actual_blob = hashlib.sha1(
                        f"blob {len(raw_bytes)}\0".encode("utf-8") + raw_bytes
                    ).hexdigest()
                if not expected_blob or expected_blob != actual_blob:
                    fail(
                        f"Image-link blob SHA mismatch: {rel(record_path)} "
                        f"expected={expected_blob} actual={actual_blob}"
                    )

                if not record.get("event_at") or not record.get("recorded_at"):
                    fail(f"Image-link missing temporal fields: {rel(record_path)}")
                if not record.get("context_refs"):
                    fail(f"Image-link missing context_refs: {rel(record_path)}")
                if not record.get("memory_refs"):
                    fail(f"Image-link missing memory_refs: {rel(record_path)}")

                for ref_key in ("context_refs", "memory_refs"):
                    for ref in record.get(ref_key, []):
                        if not (ROOT / str(ref)).exists():
                            fail(
                                f"Image-link {ref_key} points to missing source: "
                                f"{rel(record_path)} -> {ref}"
                            )

                if image_path in link_records:
                    fail(
                        f"Duplicate image-link record for {image_path}: "
                        f"{rel(link_records[image_path])}, {rel(record_path)}"
                    )
                link_records[image_path] = record_path
                covered_images.add(image_path)

                for derivative in record.get("derivative_refs", []):
                    derivative_path = str(derivative or "").strip()
                    if not derivative_path:
                        continue
                    derivative_file = ROOT / derivative_path
                    if not derivative_file.is_file():
                        fail(
                            f"Image-link derivative_refs points to missing media file: "
                            f"{rel(record_path)} -> {derivative_path}"
                        )
                    covered_images.add(derivative_path)

        missing_links = [rel(p) for p in images if rel(p) not in covered_images]
        if missing_links:
            fail(f"Images missing structured media-link records: {missing_links}")

    if CURRENT_CONTEXT_FILE.is_file() and FAST_RECALL_FILE.is_file():
        current_match = CHECKPOINT_RE.search(CURRENT_CONTEXT_FILE.read_text(encoding="utf-8"))
        fast_match = CHECKPOINT_RE.search(FAST_RECALL_FILE.read_text(encoding="utf-8"))
        if current_match and fast_match and current_match.group(0) != fast_match.group(0):
            fail(
                "Recovery entrypoints disagree on latest checkpoint: "
                f"{current_match.group(0)} != {fast_match.group(0)}"
            )

    print("OK: GPTina ownership, status overrides, visual coverage and recovery pointers are consistent.")


def main() -> None:
    ap = argparse.ArgumentParser(description="GPTina isolated long-term RAG memory")
    sub = ap.add_subparsers(dest="cmd", required=True)

    bp = sub.add_parser("build", help="Build a regenerable index under rag/index/")
    bp.add_argument("--history", action="store_true", help="Include historical git revisions")
    bp.add_argument("--no-history", action="store_true", help="Backward-compatible alias for current-only build")
    bp.add_argument(
        "--allow-dirty-preview",
        action="store_true",
        help="Explicitly build non-canonical projections from a dirty worktree",
    )

    sp = sub.add_parser("search", help="Retrieve memories")
    sp.add_argument("query")
    sp.add_argument("--top-k", type=int, default=6)
    sp.add_argument(
        "--backend",
        choices=("sqlite", "jsonl"),
        default="sqlite",
        help="Retrieval backend (default: sqlite FTS5)",
    )
    sp.add_argument(
        "--allow-dirty-preview",
        action="store_true",
        help="Explicitly query a non-canonical dirty-worktree preview",
    )
    sp.add_argument("--history", action="store_true", help="Include historical git revisions in search")
    sp.add_argument(
        "--all-statuses",
        action="store_true",
        help="Include superseded/invalidated memories (normally excluded)",
    )

    ep = sub.add_parser("find-exact", help="Find an exact phrase in current GPTina sources")
    ep.add_argument("text")
    ep.add_argument("--limit", type=int, default=20)
    ep.add_argument(
        "--backend",
        choices=("scan", "trigram"),
        default="scan",
        help="Exact backend; trigram is optional and must be built explicitly",
    )
    ep.add_argument(
        "--all-statuses",
        action="store_true",
        help="Also search superseded/invalidated memories",
    )

    lp = sub.add_parser(
        "link-image",
        help="Create a structured image-to-context/memory link record",
    )
    lp.add_argument("image_path")
    lp.add_argument("--event-at", required=True)
    lp.add_argument(
        "--status",
        required=True,
        choices=(
            "archived", "context_incomplete",
            "documented_anchor", "recognized_visual_anchor",
        ),
    )
    lp.add_argument("--event-id", required=True)
    lp.add_argument("--thread", action="append", default=[])
    lp.add_argument("--context", action="append", required=True)
    lp.add_argument("--memory", action="append", required=True)
    lp.add_argument("--cue", action="append", default=[])

    stats_parser = sub.add_parser("stats", help="Show derived SQLite index statistics")
    stats_parser.add_argument("--allow-dirty-preview", action="store_true")
    sub.add_parser("verify", help="Verify ownership, status, visual coverage and recovery pointers")
    sub.add_parser("build-exact", help="Build the optional disposable exact trigram index")

    args = ap.parse_args()
    if args.cmd == "build":
        if args.history and args.no_history:
            fail("Choose only one of --history or --no-history.")
        verify_boundary()
        stats = build_all_projections(
            include_history=bool(args.history),
            allow_dirty_preview=bool(args.allow_dirty_preview),
        )
        print(f"SQLite FTS5 sync: {stats}")
    elif args.cmd == "search":
        if args.backend == "sqlite":
            results = sqlite_search(
                args.query,
                args.top_k,
                include_historical=bool(args.history),
                include_superseded=bool(args.all_statuses),
                allow_dirty_preview=bool(args.allow_dirty_preview),
            )
            if not results:
                print("No matching memories.")
            for rank, (score, d) in enumerate(results, 1):
                print(f"\n[{rank}] score={score:.6f} id={d['chunk_id']}")
                print(
                    f"source={d['source']} revision={d['revision']} "
                    f"historical={d['historical']} status={d.get('status', 'current')}"
                )
                print(f"section={d.get('heading')}")
                print(str(d.get("text", "")).strip())
        else:
            search(
                args.query,
                args.top_k,
                include_history=bool(args.history),
                include_superseded=bool(args.all_statuses),
            )
    elif args.cmd == "find-exact":
        find_exact(
            args.text,
            include_superseded=bool(args.all_statuses),
            limit=args.limit,
            backend=args.backend,
        )
    elif args.cmd == "build-exact":
        print(json.dumps(build_exact_trigram_index(), ensure_ascii=False, indent=2))
    elif args.cmd == "link-image":
        target = create_image_link(
            args.image_path,
            args.event_at,
            args.status,
            args.event_id,
            args.thread,
            args.context,
            args.memory,
            args.cue,
        )
        print(f"Created {rel(target)}")
    elif args.cmd == "stats":
        print(json.dumps(
            sqlite_stats(allow_dirty_preview=bool(args.allow_dirty_preview)),
            ensure_ascii=False,
            indent=2,
        ))
    elif args.cmd == "verify":
        verify_boundary()


if __name__ == "__main__":
    main()
