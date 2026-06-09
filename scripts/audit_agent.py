#!/usr/bin/env python3
"""
Agente auditor histórico - fase 1.

Esta primera versión NO audita visualmente y NO escribe en Upstash.
Solo lista keys, lee envelopes y entrega resumen del universo a auditar.

Uso:
    python scripts/audit_agent.py --summary
    python scripts/audit_agent.py --summary --limit 20
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from collections import Counter
from typing import Any, Dict, List, Tuple

KEY_PATTERN = "helice:guia:numero:*"


def env_required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Falta variable de entorno: {name}")
    return value.rstrip("/")


class UpstashClient:
    def __init__(self) -> None:
        self.base_url = env_required("KV_REST_API_URL")
        self.token = env_required("KV_REST_API_TOKEN")

    def command(self, parts: List[str]) -> Any:
        encoded = "/".join(urllib.parse.quote(str(part), safe="") for part in parts)
        url = f"{self.base_url}/{encoded}"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {self.token}"})
        with urllib.request.urlopen(req, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if "error" in payload and payload["error"]:
            raise RuntimeError(payload["error"])
        return payload.get("result")

    def scan_keys(self, pattern: str = KEY_PATTERN, count: int = 100) -> List[str]:
        cursor = "0"
        keys: List[str] = []
        while True:
            result = self.command(["SCAN", cursor, "MATCH", pattern, "COUNT", str(count)])
            if not isinstance(result, list) or len(result) != 2:
                raise RuntimeError(f"Respuesta SCAN inesperada: {result}")
            cursor = str(result[0])
            batch = result[1] or []
            keys.extend(batch)
            if cursor == "0":
                break
        return sorted(set(keys))

    def get_json(self, key: str) -> Dict[str, Any]:
        raw = self.command(["GET", key])
        if raw is None:
            return {}
        if isinstance(raw, dict):
            return raw
        if isinstance(raw, str):
            return json.loads(raw)
        raise RuntimeError(f"Valor inesperado para {key}: {type(raw)}")


def summarize(envelopes: List[Tuple[str, Dict[str, Any]]]) -> Dict[str, Any]:
    providers = Counter()
    states = Counter()
    audit_states = Counter()
    steps = Counter()
    review_applied = Counter()
    duplicates = Counter()
    source_types = Counter()
    with_blob = 0
    without_blob = 0

    for _, env in envelopes:
        result = env.get("result") or {}
        data = result.get("data") or {}
        audit = env.get("audit") or {}
        ai_audit = result.get("ai_audit") or {}
        source = env.get("source") or {}
        blob = source.get("blob") or {}

        providers[result.get("proveedor_layout") or "SIN_PROVEEDOR"] += 1
        states[result.get("estado") or "SIN_ESTADO"] += 1
        audit_states[audit.get("estado") or "SIN_AUDIT"] += 1
        steps[str(ai_audit.get("stepsCount") or "SIN_STEPS")] += 1
        review_applied[str(ai_audit.get("reviewApplied", "SIN_REVIEW"))] += 1
        duplicates[str(env.get("duplicate", False))] += 1
        source_types[source.get("type") or "SIN_SOURCE_TYPE"] += 1

        if blob.get("url"):
            with_blob += 1
        else:
            without_blob += 1

        _ = data

    return {
        "total_keys_leidas": len(envelopes),
        "audit_pendientes": audit_states.get("SIN_AUDIT", 0),
        "audit_existentes": len(envelopes) - audit_states.get("SIN_AUDIT", 0),
        "con_blob_url": with_blob,
        "sin_blob_url": without_blob,
        "por_proveedor_layout": dict(providers),
        "por_estado_result": dict(states),
        "por_estado_audit": dict(audit_states),
        "por_steps_count": dict(steps),
        "por_review_applied": dict(review_applied),
        "por_duplicate": dict(duplicates),
        "por_source_type": dict(source_types),
    }


def print_summary(summary: Dict[str, Any]) -> None:
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="Agente auditor histórico - resumen inicial")
    parser.add_argument("--summary", action="store_true", help="Imprime resumen del universo auditable")
    parser.add_argument("--limit", type=int, default=0, help="Limita cantidad de keys leídas")
    args = parser.parse_args()

    if not args.summary:
        parser.error("Por ahora solo existe modo --summary")

    client = UpstashClient()
    keys = client.scan_keys()
    if args.limit and args.limit > 0:
        keys = keys[: args.limit]

    envelopes: List[Tuple[str, Dict[str, Any]]] = []
    for key in keys:
        try:
            envelopes.append((key, client.get_json(key)))
        except Exception as exc:
            envelopes.append((key, {"audit_agent_read_error": str(exc)}))

    print_summary(summarize(envelopes))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
