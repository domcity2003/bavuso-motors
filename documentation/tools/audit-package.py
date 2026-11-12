"""Regenerate the component search index and audit documentation/data integrity.

Python 3 standard library only. Run from any directory. This never validates the
physical vehicle, selected parts, engineering safety or manufacturing readiness.
Exit 0 = checks passed; exit 1 = document/data errors; no external URLs fetched.
"""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import csv
import datetime
import json
import math
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
REGISTERS = ROOT / "registers"
EXPECTED_COMPONENTS = {
    "mechanical-components.csv": 86,
    "electrical-components.csv": 42,
    "road-equipment-components.csv": 30,
}
ALIASES = {"M-038": "EL016", "RE014": "EL041", "RE015": "EL030"}
ERRORS = []
CHECKS = []


def check(name, condition, detail):
    record = {"check": name, "passed": bool(condition), "detail": detail}
    CHECKS.append(record)
    if not condition:
        ERRORS.append(record)


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames or []
        rows = list(reader)
    check("csv_headers", len(fields) == len(set(fields)) and bool(fields),
          str(path.relative_to(ROOT)))
    check("csv_row_shapes", all(None not in row and all(v is not None for v in row.values()) for row in rows),
          str(path.relative_to(ROOT)))
    return rows, fields


def get(row, *keys):
    for key in keys:
        if key in row:
            return row[key]
    return ""


def generate_index(component_data):
    indexed = []
    for filename, rows in component_data.items():
        for row in rows:
            identifier = get(row, "id", "ID")
            alias = ALIASES.get(identifier, "")
            parent = get(row, "parent", "Assembly", "assembly")
            status = get(row, "status", "Status")
            if alias:
                relationship = "Reference duplicate; use canonical record for shared hardware"
            elif parent.startswith("M-"):
                relationship = "Child/function of assembly; parent and child are not additive"
            else:
                relationship = "Assembly or function; leaf expansion and reconciliation required"
            if "OPTION" in status.upper():
                relationship += "; optional configuration"
            if "DEVELOPMENT" in status.upper() or identifier in ("RE029", "RE030"):
                relationship += "; development/tooling excludes base-vehicle mass"
            if identifier in ("RE025", "RE026", "RE027"):
                relationship += "; alternative finish already included in coated part mass"
            indexed.append({
                "record_id": identifier,
                "source_register": filename,
                "canonical_reference": alias or identifier,
                "parent_or_assembly": parent,
                "description": get(row, "description", "Function", "function"),
                "quantity_text": get(row, "quantity", "Quantity"),
                "status": status,
                "relationship": relationship,
                "mass_rollup_permitted": "False",
                "mass_owner_or_basis": get(row, "mass_bucket", "Mass_basis", "mass_owner"),
                "release_blocker": get(row, "release_blocker", "Release_blocker", "definition_required"),
            })
    path = REGISTERS / "component-index.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(indexed[0]))
        writer.writeheader()
        writer.writerows(indexed)
    identifiers = {row["record_id"] for row in indexed}
    check("component_index_count", len(indexed) == 158,
          f"{len(indexed)} indexed records, not selected parts or additive quantities")
    check("component_index_ids", len(identifiers) == len(indexed), "IDs unique across component registers")
    check("canonical_aliases", all(a in identifiers and c in identifiers for a, c in ALIASES.items()),
          ALIASES)
    return indexed


def local_link_target(raw, markdown):
    raw = raw.strip()
    if raw.startswith("<") and ">" in raw:
        raw = raw[1:raw.index(">")]
    else:
        # Support optional Markdown title without splitting literal path spaces.
        raw = re.sub(r'\s+["\'][^"\']*["\']\s*$', "", raw)
    raw = unquote(raw)
    if not raw or raw.startswith("#"):
        return None
    windows_absolute = bool(re.match(r"^[A-Za-z]:[\\/]", raw))
    if windows_absolute:
        clean = raw.split("#", 1)[0].split("?", 1)[0]
        return Path(clean)
    parsed = urlsplit(raw)
    if parsed.scheme or parsed.netloc:
        return None
    clean = parsed.path
    if not clean:
        return None
    path = Path(clean)
    return path if path.is_absolute() else markdown.parent / path


def audit_links():
    # Inline Markdown links/images and reference definitions. Fragments are not
    # checked; neither external servers nor Markdown heading anchors are tested.
    pattern = re.compile(r"!?\[[^\]\n]*\]\((<[^>]+>|[^)\n]+)\)")
    reference = re.compile(r"^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)", re.MULTILINE)
    files = sorted(ROOT.rglob("*.md"))
    checked = 0
    broken = []
    for markdown in files:
        content = markdown.read_text(encoding="utf-8-sig")
        # Code fences contain illustrative paths, not rendered links.
        content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
        for match in list(pattern.finditer(content)) + list(reference.finditer(content)):
            raw = match.group(1)
            target = local_link_target(raw, markdown)
            if target is None:
                continue
            checked += 1
            if not target.exists():
                broken.append({"document": str(markdown.relative_to(ROOT)), "link": raw,
                               "resolved": str(target.resolve())})
    check("local_markdown_links", not broken,
          {"markdown_files": len(files), "local_targets_checked": checked, "broken": broken,
           "scope": "Existence only; no heading-anchor or external-link validation"})


def close(a, b):
    return math.isclose(float(a), float(b), rel_tol=1e-8, abs_tol=1e-7)


def audit_model(csv_data):
    rows = csv_data.get("research/configuration-trades.csv", [])
    summary_path = ROOT / "models/development-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8-sig"))
    check("configuration_count", len(rows) == 72 == summary["configuration_cases"], len(rows))
    check("summary_requirements", summary["requirements"] == len(csv_data.get("registers/requirements.csv", [])),
          summary["requirements"])
    check("summary_interfaces", summary["interfaces"] == len(csv_data.get("registers/interfaces.csv", [])),
          summary["interfaces"])
    check("summary_conflict_count", summary["packaging_conflicts"] == len(csv_data.get("registers/packaging-conflicts.csv", [])),
          "Conflict count only; does not prove clearance coverage")
    failures = []
    for i, row in enumerate(rows, 1):
        cells = int(row["series"]) * int(row["parallel"])
        cell_mass = cells * 0.0973
        pack = cell_mass / float(row["cell_fraction"])
        bike = pack + float(row["nonpack_kg"])
        allowance_mass = bike + 0.05 * (bike - cell_mass)
        speed = 70 * 1609.344 / 3600
        force = 0.5 * 1.225 * float(row["cda"]) * speed ** 2
        force += 0.015 * (bike + 90) * 9.80665
        # Independent energy-per-distance expression, converted from J/m to Wh/mi.
        joules_per_metre = force / 0.9 + 300 / speed
        wh_per_mile = joules_per_metre * 1609.344 / 3600
        computed = {
            "cells": cells, "typical_kwh": cells * 37.57 / 1000,
            "minimum_kwh": cells * 36.72 / 1000, "pack_kg": pack,
            "bike_lb": bike / 0.45359237,
            "bike_with_allowance_lb": allowance_mass / 0.45359237,
            "range_70_mi": cells * 37.57 * 0.9 / wh_per_mile,
            "range_70_90pct_soh_mi": cells * 37.57 * 0.9 * 0.9 / wh_per_mile,
            "range_70_minimum_cell_wh_mi": cells * 36.72 * 0.9 / wh_per_mile,
            "typical_charge_a": int(row["parallel"]) * 10.8,
            "maximum_charge_a": int(row["parallel"]) * 21.6,
            "cell_a_at_70kw_250v": 70000 / 250 / int(row["parallel"]),
        }
        for key, value in computed.items():
            if not close(row[key], value):
                failures.append({"row": i, "field": key, "stored": row[key], "recomputed": value})
        for key, expected in (
            ("meets_mass_with_allowance", allowance_mass / 0.45359237 < 400),
            ("meets_screened_range", computed["range_70_mi"] >= 200),
        ):
            if row[key].lower() != str(expected).lower():
                failures.append({"row": i, "field": key, "stored": row[key], "recomputed": expected})
    check("independent_screening_arithmetic", not failures,
          {"rows_checked": len(rows), "failures": failures,
           "scope": "Given assumptions only; supplier and physical performance unverified"})
    for name in ("aero_led_focused", "aero_led_reference", "aero_led_stretch"):
        case = summary[name]
        matching = [row for row in rows if int(row["cells"]) == case["cells"]
                    and row["basis"] == case["basis"] and close(row["cda"], case["cda"])]
        check("summary_case_" + name,
              len(matching) == 1 and all(close(matching[0][field], case[field])
                                        for field in ("typical_kwh", "bike_with_allowance_lb", "range_70_mi")),
              "Summary reproduces an exported scenario; not evidence goals achieved")


def main():
    data = {}
    for path in sorted(ROOT.rglob("*.csv")):
        if path.name == "component-index.csv":
            continue
        rows, fields = read_csv(path)
        data[path.relative_to(ROOT).as_posix()] = rows
        id_field = "id" if "id" in fields else "ID" if "ID" in fields else None
        if id_field:
            identifiers = [row[id_field] for row in rows]
            check("csv_identifiers", all(identifiers) and len(identifiers) == len(set(identifiers)),
                  str(path.relative_to(ROOT)))
    component_data = {}
    for filename, expected in EXPECTED_COMPONENTS.items():
        rows = data["registers/" + filename]
        component_data[filename] = rows
        check("component_register_count", len(rows) == expected,
              {"register": filename, "actual": len(rows), "expected": expected})
    indexed = generate_index(component_data)
    audit_links()
    audit_model(data)
    result = {
        "schema_version": 1,
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "PASS_DOCUMENTATION_DATA_CHECKS" if not ERRORS else "FAIL_DOCUMENTATION_DATA_CHECKS",
        "scope": "Document existence, CSV structure/identifiers, explicit index aliases and screening arithmetic only",
        "physical_verification_performed": False,
        "manufacturing_release": False,
        "engineering_goals_proven": False,
        "component_index_records": len(indexed),
        "component_records_are_selected_parts": False,
        "mass_rollup_authorized": False,
        "canonical_reference_aliases": ALIASES,
        "checks": CHECKS,
        "error_count": len(ERRORS),
    }
    target = ROOT / "verification/documentation-audit.json"
    target.parent.mkdir(exist_ok=True, parents=True)
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"{result['status']}: {len(CHECKS)} checks, {len(ERRORS)} errors; {len(indexed)} indexed records.")
    print("Scope: documentation/data integrity only; no physical verification or build release.")
    for error in ERRORS:
        print(json.dumps(error, ensure_ascii=False))
    return 1 if ERRORS else 0


if __name__ == "__main__":
    sys.exit(main())
