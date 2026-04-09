#!/usr/bin/env python3
"""
Convert RIS bibliography files to Morsor collection JSON (littlePrinceItem items).

Each input file becomes one collection document:
  { "id", "name", "shortName", "items": [ { "littlePrinceItem": { ... } }, ... ] }

Accepts any number of paths ending in .ris or .rsi (same line-oriented RIS format).
Writes <basename>.json next to each input file.

Usage:
  ./ris-to-little-prince-collection.py ../moocho-data/Reading.ris
  ./ris-to-little-prince-collection.py *.rsi
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

TAG_LINE = re.compile(r"^([A-Z0-9]{2})\s+-\s?(.*)$")

script_name = Path(__file__).stem


def die(msg: str, code: int = 2) -> None:
    print(f"{script_name}: {msg}", file=sys.stderr)
    sys.exit(code)

def parse_ris(text: str) -> list[dict[str, list[str]]]:
    """Split RIS text into records; each record maps tag -> list of values (multiline folded)."""
    records: list[dict[str, list[str]]] = []
    rec: dict[str, list[str]] = {}
    last_tag: str | None = None

    for raw in text.splitlines():
        line = raw.rstrip("\r")
        if not line:
            continue
        m = TAG_LINE.match(line)
        if m:
            tag, rest = m.group(1), m.group(2)
            if tag == "ER":
                if rec:
                    records.append(rec)
                rec = {}
                last_tag = None
                continue
            last_tag = tag
            rec.setdefault(tag, []).append(rest)
        elif last_tag:
            rec[last_tag][-1] = (rec[last_tag][-1] + " " + line).strip()

    if rec:
        records.append(rec)
    return records


def _first(rec: dict[str, list[str]], *tags: str) -> str | None:
    for t in tags:
        vals = rec.get(t)
        if vals:
            s = vals[0].strip()
            if s:
                return s
    return None


def _all_join(rec: dict[str, list[str]], *tags: str, sep: str = ", ") -> str | None:
    parts: list[str] = []
    for t in tags:
        for v in rec.get(t, []):
            s = v.strip()
            if s:
                parts.append(s)
    return sep.join(parts) if parts else None


def normalize_date_added(da: str) -> str:
    """RIS often uses YYYY/MM/DD or YYYY/M/D; fixtures use YYYY-MM-DD."""
    da = da.strip()
    for sep in ("/", "-", " "):
        if sep in da:
            bits = [b for b in re.split(r"[/\s-]+", da) if b]
            if len(bits) >= 3 and bits[0].isdigit() and len(bits[0]) == 4:
                y, mo, d = bits[0], bits[1].zfill(2), bits[2].zfill(2)
                return f"{y}-{mo}-{d}"
            if len(bits) == 1 and bits[0].isdigit() and len(bits[0]) == 4:
                return f"{bits[0]}-01-01"
    if re.fullmatch(r"\d{4}", da):
        return f"{da}-01-01"
    return da


def ris_record_to_item(rec: dict[str, list[str]]) -> dict[str, Any] | None:
    """
    Map one RIS record to a littlePrinceItem object (inner fields only).
    Morsor requires a non-empty 'title' property on each item.
    """
    title = _first(rec, "TI", "T1")
    if not title:
        return None

    item: dict[str, Any] = {"title": title}

    t2 = _first(rec, "T2", "BT")
    if t2:
        item["display-title"] = f"{title}: {t2}"

    author = _all_join(rec, "AU", "A1", "A2", "A3", "A4")
    if author:
        item["author"] = author

    ed = _all_join(rec, "ED", "A6")
    if ed:
        item["editor"] = ed

    py = _first(rec, "PY", "Y1")
    if py:
        year = py.split("/")[0].strip()
        if year:
            item["year"] = year

    da = _first(rec, "DA", "Y2")
    if da:
        item["date-added"] = normalize_date_added(da)

    la = _first(rec, "LA")
    if la:
        item["language"] = la

    pb = _first(rec, "PB")
    if pb:
        item["publisher"] = pb

    cy = _first(rec, "CY")
    if cy:
        item["publication-location"] = cy

    sn = _first(rec, "SN")
    if sn:
        item["isbn13"] = sn.strip()

    ur = _first(rec, "UR", "L1", "LK")
    if ur:
        item["itemUrl"] = ur.strip()

    ty = _first(rec, "TY")
    if ty:
        item["ris-type"] = ty

    ab = _all_join(rec, "AB", "N2", sep=" ")
    if ab:
        item["abstract"] = ab

    doi = _first(rec, "DO")
    if doi:
        item["doi"] = doi

    jf = _first(rec, "JF", "JO", "T3")
    if jf:
        item["journal"] = jf

    vl = _first(rec, "VL")
    if vl:
        item["volume"] = vl

    is_ = _first(rec, "IS")
    if is_:
        item["issue"] = is_

    sp = _first(rec, "SP")
    ep = _first(rec, "EP")
    if sp or ep:
        if sp and ep:
            item["pages"] = f"{sp}–{ep}"
        else:
            item["pages"] = sp or ep

    consumed = {
        "TI",
        "T1",
        "T2",
        "BT",
        "AU",
        "A1",
        "A2",
        "A3",
        "A4",
        "A6",
        "ED",
        "PY",
        "Y1",
        "DA",
        "Y2",
        "LA",
        "PB",
        "CY",
        "SN",
        "UR",
        "L1",
        "LK",
        "TY",
        "AB",
        "N2",
        "DO",
        "JF",
        "JO",
        "T3",
        "VL",
        "IS",
        "SP",
        "EP",
        "ER",
    }
    for tag, vals in rec.items():
        if tag in consumed:
            continue
        joined = "; ".join(v.strip() for v in vals if v and v.strip())
        if joined:
            item[f"ris-{tag.lower()}"] = joined

    return item


def collection_id_from_stem(stem: str) -> str:
    s = stem.strip()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^a-zA-Z0-9_-]+", "-", s)
    s = s.strip("-").lower()
    return s or "ris-collection"


def build_collection(path: Path, items: list[dict[str, Any]]) -> dict[str, Any]:
    stem = path.stem
    cid = collection_id_from_stem(stem)
    return {
        "id": cid,
        "name": stem.replace("_", " "),
        "shortName": stem if len(stem) <= 48 else stem[:45] + "…",
        "items": [{"littlePrinceItem": it} for it in items],
    }


def convert_file(path: Path) -> Path:
    text = path.read_text(encoding="utf-8", errors="replace")
    records = parse_ris(text)
    items: list[dict[str, Any]] = []
    skipped = 0
    for i, rec in enumerate(records):
        item = ris_record_to_item(rec)
        if item is None:
            skipped += 1
            print(
                f"{script_name}: skip record {i + 1} in {path.name} (no TI/T1 title)",
                file=sys.stderr,
            )
            continue
        items.append(item)

    out_path = path.with_suffix(".json")
    doc = build_collection(path, items)
    out_path.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{path} -> {out_path} ({len(items)} items, {skipped} skipped)")
    return out_path


def main(argv: list[str]) -> None:
    if len(argv) < 1:
        die(f"usage: {script_name} file.ris ...")

    for arg in argv:
        path = Path(arg)
        if not path.is_file():
            die(f"not a file: {arg}")
        suf = path.suffix.lower()
        if suf not in (".ris"):
            print(f"WARNING: Expected .ris extension: {arg}. Trying to parse as RIS format anyway", file=sys.stderr)
        convert_file(path)


if __name__ == "__main__":
    main(sys.argv[1:])
