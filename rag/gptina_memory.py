#!/usr/bin/env python3
"""GPTina long-term RAG memory.

Canonical repository files are READ-ONLY inputs.
This program writes only inside rag/index/.
No external Python dependencies are required.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import math
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
RAG_ROOT = ROOT / "rag"
INDEX_DIR = RAG_ROOT / "index"
INDEX_FILE = INDEX_DIR / "memory_chunks.jsonl"
META_FILE = INDEX_DIR / "index_meta.json"
MANIFEST_FILE = RAG_ROOT / "memory_manifest.json"
VISUAL_INDEX_FILE = INDEX_DIR / "GPTINA_VISUAL_CHRONOLOGY.md"
CURRENT_CONTEXT_FILE = INDEX_DIR / "CURRENT_CONTEXT.md"
FAST_RECALL_FILE = INDEX_DIR / "GPTINA_FAST_RECALL.md"
TOKEN_RE = re.compile(r"[0-9A-Za-zÀ-ÖØ-öø-ÿ_]+", re.UNICODE)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
DATE_RE = re.compile(r"(20\d{2})[-_](\d{2})[-_](\d{2})")
COMPACT_DATE_RE = re.compile(r"(20\d{2})(\d{2})(\d{2})")
CHECKPOINT_RE = re.compile(r"checkpoints/[A-Za-z0-9_.-]+\.md")
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
MONTHS_IT = {
    "gennaio": "01", "febbraio": "02", "marzo": "03", "aprile": "04",
    "maggio": "05", "giugno": "06", "luglio": "07", "agosto": "08",
    "settembre": "09", "ottobre": "10", "novembre": "11", "dicembre": "12",
}
MEMORY_SCHEMA_REQUIRED_KEYS = (
    "schema_version:", "memory_id:", "owner:", "event_at:", "recorded_at:",
    "status:", "confidence:", "source_refs:", "media_refs:",
)


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


def current_source_fingerprint(manifest: dict) -> str:
    rows: list[str] = []
    for path, _spec in expand_sources(manifest):
        rp = rel(path)
        rows.append(f"{rp}\0{sha256_text(decode_source(path))}")
    return sha256_text("\n".join(sorted(rows)))


def memory_status(path: str, manifest: dict, content: str) -> tuple[str, str | None]:
    override = manifest.get("status_overrides", {}).get(path)
    if override:
        return str(override.get("status", "current")), override.get("replaced_by")

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
    versions: list[SourceVersion] = []
    for path, spec in expand_sources(manifest):
        rp = rel(path)
        content = decode_source(path)
        current_hash = sha256_text(content)
        kind = spec.get("kind", "source")
        priority = float(spec.get("priority", 1.0))
        status, replaced_by = memory_status(rp, manifest, content)

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


def build(include_history: bool = False) -> None:
    manifest = load_manifest()
    cfg = manifest.get("chunking", {})
    max_chars = int(cfg.get("max_chars", 1400))
    overlap = int(cfg.get("overlap_chars", 220))
    min_chars = int(cfg.get("min_chars", 120))

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
) -> list[dict]:
    target = needle.casefold()
    if not target:
        return []

    manifest = load_manifest()
    hits: list[dict] = []
    for path, spec in expand_sources(manifest):
        rp = rel(path)
        content = decode_source(path)
        status, replaced_by = memory_status(rp, manifest, content)
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


def find_exact(needle: str, include_superseded: bool, limit: int) -> None:
    hits = exact_matches(needle, include_superseded=include_superseded, limit=limit)
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


def verify_future_memory_schema(manifest: dict) -> None:
    cutoff = str(manifest.get("policy", {}).get("memory_schema_required_from", "")).strip()
    if not cutoff:
        return

    memories = RAG_ROOT / "memories" / "gptina"
    if not memories.is_dir():
        return

    errors: list[str] = []
    for path in sorted(memories.rglob("*.md")):
        rp = rel(path)
        date_hint = extract_date(rp)
        if not date_hint or date_hint < cutoff:
            continue
        raw = path.read_text(encoding="utf-8")
        for key in MEMORY_SCHEMA_REQUIRED_KEYS:
            if key not in raw[:2200]:
                errors.append(f"{rp}: missing {key}")
        if "owner: gptina" not in raw[:2200]:
            errors.append(f"{rp}: owner must be gptina")
    if errors:
        fail("Future memory schema violations:\n- " + "\n- ".join(errors))


def verify_boundary() -> None:
    """Verify ownership, index boundaries, image coverage and recovery pointers."""
    manifest = load_manifest()
    policy = manifest.get("policy", {})
    ok = bool(policy.get("canonical_sources_are_immutable_inputs")) and not bool(policy.get("destructive_compaction"))
    if not ok:
        fail("Manifest violates immutable-source policy.")

    for p in (INDEX_FILE, META_FILE):
        ensure_inside_rag(p)

    verify_future_memory_schema(manifest)

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

    sp = sub.add_parser("search", help="Retrieve memories")
    sp.add_argument("query")
    sp.add_argument("--top-k", type=int, default=6)
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
        "--all-statuses",
        action="store_true",
        help="Also search superseded/invalidated memories",
    )

    sub.add_parser("verify", help="Verify ownership, status, visual coverage and recovery pointers")

    args = ap.parse_args()
    if args.cmd == "build":
        if args.history and args.no_history:
            fail("Choose only one of --history or --no-history.")
        verify_boundary()
        build(include_history=bool(args.history))
    elif args.cmd == "search":
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
        )
    elif args.cmd == "verify":
        verify_boundary()


if __name__ == "__main__":
    main()
