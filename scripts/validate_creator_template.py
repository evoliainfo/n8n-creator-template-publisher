#!/usr/bin/env python3
"""
Static validator for n8n Creator/community workflow JSON files.

This script intentionally does not enforce a numeric sticky-note text limit.
n8n reviewer guidance supplied to the skill says those limits are changing,
and no authoritative numeric range was provided.

Usage:
  python validate_creator_template.py workflow.json
  python validate_creator_template.py candidate.json --report qa.json
  python validate_creator_template.py candidate.json \
      --baseline baseline.json --require-functional-match --report qa.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

STICKY_TYPE = "n8n-nodes-base.stickyNote"

DEFAULT_FUNCTION_NAMES = {
    "http request", "code", "set", "edit fields", "if", "switch",
    "merge", "no operation, do nothing", "wait", "loop over items",
    "split in batches", "wordpress", "gmail", "google sheets", "notion"
}

SECRET_PATTERNS = {
    "google_api_key": re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b"),
    "openai_style_key": re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "bearer_token": re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/\-=]{20,}"),
}

EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
INTERNAL_TITLE_RE = re.compile(r"(?i)(?:^|[\s_-])(final|approved|community\s+final|hardened|v\d+(?:\.\d+){0,2})(?:$|[\s_-])")

REF_PATTERNS = [
    re.compile(r"""\$\((['"])(.*?)\1\)"""),
    re.compile(r"""\$node\[\s*(['"])(.*?)\1\s*\]"""),
    re.compile(r"""\$items\(\s*(['"])(.*?)\1"""),
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("workflow", type=Path)
    p.add_argument("--baseline", type=Path)
    p.add_argument("--require-functional-match", action="store_true")
    p.add_argument("--report", type=Path)
    return p.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Workflow JSON root must be an object")
    return data


def validate_workflow_shape(wf: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if not isinstance(wf.get("name"), str) or not wf.get("name", "").strip():
        issues.append("workflow_name_missing_or_invalid")

    nodes = wf.get("nodes")
    if not isinstance(nodes, list):
        issues.append("nodes_not_list")
        return issues

    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            issues.append(f"node_{index}_not_object")
            continue
        if not isinstance(node.get("id"), str) or not node.get("id", "").strip():
            issues.append(f"node_{index}_missing_or_invalid_id")
        if not isinstance(node.get("name"), str) or not node.get("name", "").strip():
            issues.append(f"node_{index}_missing_or_invalid_name")
        if not isinstance(node.get("type"), str) or not node.get("type", "").strip():
            issues.append(f"node_{index}_missing_or_invalid_type")

    if not isinstance(wf.get("connections", {}), dict):
        issues.append("connections_not_object")
    if "settings" in wf and not isinstance(wf.get("settings"), dict):
        issues.append("settings_not_object")
    if "meta" in wf and not isinstance(wf.get("meta"), dict):
        issues.append("meta_not_object")
    return issues


def functional_nodes(wf: dict[str, Any]) -> list[dict[str, Any]]:
    return [n for n in wf.get("nodes", []) if isinstance(n, dict) and n.get("type") != STICKY_TYPE]


def sticky_nodes(wf: dict[str, Any]) -> list[dict[str, Any]]:
    return [n for n in wf.get("nodes", []) if isinstance(n, dict) and n.get("type") == STICKY_TYPE]


def walk_strings(value: Any):
    if isinstance(value, dict):
        for v in value.values():
            yield from walk_strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from walk_strings(v)
    elif isinstance(value, str):
        yield value


def explicit_node_refs(wf: dict[str, Any]) -> set[str]:
    refs: set[str] = set()
    for n in functional_nodes(wf):
        for s in walk_strings(n.get("parameters", {})):
            for pat in REF_PATTERNS:
                for m in pat.finditer(s):
                    refs.add(m.group(2))
    return refs


def connection_issues(wf: dict[str, Any]) -> list[dict[str, str]]:
    names = {n.get("name") for n in functional_nodes(wf)}
    issues = []
    for source, by_type in wf.get("connections", {}).items():
        if source not in names:
            issues.append({"kind": "missing_source", "name": source})
        if not isinstance(by_type, dict):
            continue
        for branches in by_type.values():
            if not isinstance(branches, list):
                continue
            for branch in branches:
                if not isinstance(branch, list):
                    continue
                for conn in branch:
                    target = conn.get("node")
                    if target not in names:
                        issues.append({"kind": "missing_target", "name": str(target)})
    return issues


def unresolved_refs(wf: dict[str, Any]) -> list[str]:
    names = {n.get("name") for n in functional_nodes(wf)}
    return sorted(r for r in explicit_node_refs(wf) if r not in names)


def duplicate_values(values: list[Any]) -> list[Any]:
    seen, dup = set(), []
    for v in values:
        if v in seen and v not in dup:
            dup.append(v)
        seen.add(v)
    return dup


def private_leak_checks(wf: dict[str, Any]) -> dict[str, Any]:
    serialized = json.dumps(wf, ensure_ascii=False)
    hits = {name: bool(p.search(serialized)) for name, p in SECRET_PATTERNS.items()}

    credential_nodes = [
        n.get("name") for n in functional_nodes(wf)
        if isinstance(n.get("credentials"), dict) and n.get("credentials")
    ]

    webhook_nodes = [
        n.get("name") for n in functional_nodes(wf)
        if n.get("webhookId")
    ]

    hardcoded_emails = []
    for s in walk_strings(wf):
        if "__PLACEHOLDER_VALUE__" in s or "example.com" in s:
            continue
        for email in EMAIL_RE.findall(s):
            if email not in hardcoded_emails:
                hardcoded_emails.append(email)

    return {
        "secret_pattern_hits": hits,
        "credential_nodes": credential_nodes,
        "meta_instance_id_present": bool(wf.get("meta", {}).get("instanceId")),
        "webhook_id_nodes": webhook_nodes,
        "hardcoded_emails": hardcoded_emails,
        "error_workflow_id_present": bool(wf.get("settings", {}).get("errorWorkflow")),
        "pin_data_present": bool(wf.get("pinData")),
        "top_level_identifiers_for_review": [
            key for key in ("id", "versionId") if wf.get(key) not in (None, "")
        ],
    }


def sticky_overlap(a: dict[str, Any], b: dict[str, Any]) -> bool:
    pa, pb = a.get("position"), b.get("position")
    if not (isinstance(pa, list) and len(pa) >= 2 and isinstance(pb, list) and len(pb) >= 2):
        return False
    aa, bb = a.get("parameters", {}), b.get("parameters", {})
    wa, ha = float(aa.get("width", 0) or 0), float(aa.get("height", 0) or 0)
    wb, hb = float(bb.get("width", 0) or 0), float(bb.get("height", 0) or 0)
    if min(wa, ha, wb, hb) <= 0:
        return False
    ax1, ay1 = float(pa[0]), float(pa[1])
    ax2, ay2 = ax1 + wa, ay1 + ha
    bx1, by1 = float(pb[0]), float(pb[1])
    bx2, by2 = bx1 + wb, by1 + hb
    return ax1 < bx2 and ax2 > bx1 and ay1 < by2 and ay2 > by1


def sticky_report(wf: dict[str, Any]) -> dict[str, Any]:
    stickies = sticky_nodes(wf)
    overlaps = []
    for i, a in enumerate(stickies):
        for b in stickies[i + 1:]:
            if sticky_overlap(a, b):
                overlaps.append([a.get("name"), b.get("name")])

    main_candidates = [
        n for n in stickies
        if "color" not in n.get("parameters", {})
    ]
    main = main_candidates[0] if len(main_candidates) == 1 else None
    main_content = str(main.get("parameters", {}).get("content", "")) if main else ""

    section_word_counts = {}
    for n in stickies:
        if n is main:
            continue
        content = str(n.get("parameters", {}).get("content", ""))
        section_word_counts[n.get("name", "")] = len(re.findall(r"\b\w+\b", content))

    return {
        "count": len(stickies),
        "main_default_color_candidates": [n.get("name") for n in main_candidates],
        "main_has_how_it_works": "### How it works" in main_content,
        "main_has_setup_steps": "### Setup steps" in main_content,
        "main_has_customization": "### Customization" in main_content,
        "section_nonwhite_nodes": [
            n.get("name") for n in stickies
            if n is not main and n.get("parameters", {}).get("color") != 7
        ],
        "section_word_counts_for_review": section_word_counts,
        "overlaps": overlaps,
        "numeric_text_limit_enforced": False,
    }


def naming_report(wf: dict[str, Any], path: Path) -> dict[str, Any]:
    vague = []
    for n in functional_nodes(wf):
        name = str(n.get("name", "")).strip()
        low = name.lower()
        if not name or low in DEFAULT_FUNCTION_NAMES or re.fullmatch(
            r"(code|set|if|http request|node|sticky note)\s*\d*", low
        ):
            vague.append(name)

    expected_slug = re.sub(r"[^a-z0-9]+", "-", str(wf.get("name", "")).lower()).strip("-") + ".json"
    title = str(wf.get("name", "")).strip()
    return {
        "workflow_name": wf.get("name"),
        "workflow_title_empty": not bool(title),
        "workflow_title_has_internal_suffix": bool(INTERNAL_TITLE_RE.search(title)),
        "vague_functional_node_names": vague,
        "filename": path.name,
        "expected_slug_from_title": expected_slug,
        "filename_matches_slug": path.name == expected_slug,
        "filename_contains_percent20": "%20" in path.name,
        "filename_contains_space": " " in path.name,
    }


def normalize_ref_string(s: str, name_to_id: dict[str, str]) -> str:
    patterns = [
        re.compile(r"""\$\((['"])(.*?)\1\)"""),
        re.compile(r"""\$node\[\s*(['"])(.*?)\1\s*\]"""),
        re.compile(r"""\$items\(\s*(['"])(.*?)\1"""),
    ]
    for pat in patterns:
        def repl(m):
            name = m.group(2)
            node_id = name_to_id.get(name, name)
            whole = m.group(0)
            return whole.replace(name, f"__NODE_ID__{node_id}")
        s = pat.sub(repl, s)
    return s


def normalize_value(v: Any, name_to_id: dict[str, str]) -> Any:
    if isinstance(v, dict):
        return {k: normalize_value(val, name_to_id) for k, val in sorted(v.items())}
    if isinstance(v, list):
        return [normalize_value(x, name_to_id) for x in v]
    if isinstance(v, str):
        return normalize_ref_string(v, name_to_id)
    return v


def semantic_node_map(wf: dict[str, Any]) -> dict[str, Any]:
    f = functional_nodes(wf)
    name_to_id = {str(n.get("name")): str(n.get("id")) for n in f}
    result = {}
    for n in f:
        node_id = str(n.get("id"))
        result[node_id] = {
            "type": n.get("type"),
            "typeVersion": n.get("typeVersion"),
            "parameters": normalize_value(n.get("parameters", {}), name_to_id),
            "disabled": n.get("disabled", False),
            "onError": n.get("onError"),
            "retryOnFail": n.get("retryOnFail"),
            "maxTries": n.get("maxTries"),
            "waitBetweenTries": n.get("waitBetweenTries"),
            "alwaysOutputData": n.get("alwaysOutputData"),
            "executeOnce": n.get("executeOnce"),
            "continueOnFail": n.get("continueOnFail"),
        }
    return result


def connection_topology_by_id(wf: dict[str, Any]) -> list[tuple]:
    f = functional_nodes(wf)
    name_to_id = {str(n.get("name")): str(n.get("id")) for n in f}
    edges = []
    for source, by_type in wf.get("connections", {}).items():
        src_id = name_to_id.get(source, source)
        for ctype, branches in by_type.items():
            for source_index, branch in enumerate(branches):
                for conn in branch:
                    tgt_id = name_to_id.get(conn.get("node"), conn.get("node"))
                    edges.append((src_id, ctype, source_index, tgt_id, conn.get("index", 0)))
    return sorted(edges)


def comparable_workflow_settings(wf: dict[str, Any]) -> dict[str, Any]:
    settings = dict(wf.get("settings", {}) or {})
    # errorWorkflow is intentionally instance-specific and is expected to be removed
    # from a public Creator/community candidate. Other settings are compared because
    # they can affect execution semantics, availability, or caller behavior.
    settings.pop("errorWorkflow", None)
    return normalize_value(settings, {})


def baseline_report(candidate: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    cand_ids = {str(n.get("id")) for n in functional_nodes(candidate)}
    base_ids = {str(n.get("id")) for n in functional_nodes(baseline)}
    return {
        "functional_node_ids_match": cand_ids == base_ids,
        "connection_topology_by_id_matches":
            connection_topology_by_id(candidate) == connection_topology_by_id(baseline),
        "functional_semantics_match":
            semantic_node_map(candidate) == semantic_node_map(baseline),
        "workflow_settings_match":
            comparable_workflow_settings(candidate) == comparable_workflow_settings(baseline),
    }


def main() -> int:
    args = parse_args()
    try:
        wf = load_json(args.workflow)
    except Exception as e:
        report = {"valid_json": False, "error": str(e), "pass": False}
        print(json.dumps(report, indent=2))
        if args.report:
            args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return 2

    shape_issues = validate_workflow_shape(wf)
    nodes = wf.get("nodes", []) if isinstance(wf.get("nodes", []), list) else []
    dict_nodes = [n for n in nodes if isinstance(n, dict)]
    ids = [n.get("id") for n in dict_nodes]
    names = [n.get("name") for n in dict_nodes]

    leaks = private_leak_checks(wf)
    stickies = sticky_report(wf)
    naming = naming_report(wf, args.workflow)

    report: dict[str, Any] = {
        "valid_json": True,
        "workflow_name": wf.get("name"),
        "active": wf.get("active"),
        "workflow_shape_issues": shape_issues,
        "functional_node_count": len(functional_nodes(wf)),
        "sticky_note_count": len(sticky_nodes(wf)),
        "duplicate_node_ids": duplicate_values(ids),
        "duplicate_node_names": duplicate_values(names),
        "connection_issues": connection_issues(wf),
        "unresolved_node_references": unresolved_refs(wf),
        "naming": naming,
        "stickies": stickies,
        "community_safety": leaks,
        "templateCredsSetupCompleted": wf.get("meta", {}).get("templateCredsSetupCompleted"),
    }

    if args.baseline:
        try:
            baseline = load_json(args.baseline)
            report["baseline"] = baseline_report(wf, baseline)
        except Exception as e:
            report["baseline"] = {"error": str(e)}

    hard_failures = []

    if report["workflow_shape_issues"]:
        hard_failures.append("workflow_shape_issues")
    if report["duplicate_node_ids"]:
        hard_failures.append("duplicate_node_ids")
    if report["duplicate_node_names"]:
        hard_failures.append("duplicate_node_names")
    if report["connection_issues"]:
        hard_failures.append("connection_issues")
    if report["unresolved_node_references"]:
        hard_failures.append("unresolved_node_references")
    if naming["workflow_title_empty"]:
        hard_failures.append("workflow_title_missing")
    if naming["workflow_title_has_internal_suffix"]:
        hard_failures.append("workflow_title_has_internal_suffix")
    if naming["vague_functional_node_names"]:
        hard_failures.append("vague_functional_node_names")
    if naming["filename_contains_percent20"] or naming["filename_contains_space"]:
        hard_failures.append("unsafe_filename_format")
    if not naming["filename_matches_slug"]:
        hard_failures.append("filename_not_canonical_slug")
    if stickies["count"] == 0:
        hard_failures.append("missing_sticky_notes")
    if len(stickies["main_default_color_candidates"]) != 1:
        hard_failures.append("main_sticky_ambiguous")
    if not stickies["main_has_how_it_works"]:
        hard_failures.append("main_missing_how_it_works")
    if not stickies["main_has_setup_steps"]:
        hard_failures.append("main_missing_setup_steps")
    if not stickies["main_has_customization"]:
        hard_failures.append("main_missing_customization")
    if stickies["section_nonwhite_nodes"]:
        hard_failures.append("section_sticky_internal_standard_not_met")
    if stickies["overlaps"]:
        hard_failures.append("sticky_overlap")

    if any(leaks["secret_pattern_hits"].values()):
        hard_failures.append("secret_pattern_hit")
    if leaks["credential_nodes"]:
        hard_failures.append("credential_bindings_present")
    if leaks["meta_instance_id_present"]:
        hard_failures.append("meta_instance_id_present")
    if leaks["webhook_id_nodes"]:
        hard_failures.append("webhook_ids_present")
    if leaks["hardcoded_emails"]:
        hard_failures.append("hardcoded_emails_present")
    if leaks["error_workflow_id_present"]:
        hard_failures.append("instance_error_workflow_present")

    if wf.get("active") is True:
        hard_failures.append("workflow_active")
    if wf.get("meta", {}).get("templateCredsSetupCompleted") is not False:
        hard_failures.append("templateCredsSetupCompleted_not_false")

    if args.require_functional_match:
        base = report.get("baseline")
        if not isinstance(base, dict) or "error" in base:
            hard_failures.append("baseline_required_but_unavailable")
        else:
            for key in (
                "functional_node_ids_match",
                "connection_topology_by_id_matches",
                "functional_semantics_match",
                "workflow_settings_match",
            ):
                if not base.get(key):
                    hard_failures.append(key)

    report["hard_failures"] = hard_failures
    report["pass"] = not hard_failures
    report["note"] = (
        "Static automated QA only. No numeric sticky text limit is enforced. "
        "Private IDs/domains, pinned sample data, behavioral truthfulness, and current n8n "
        "Creator Hub guidance still require manual review."
    )

    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
