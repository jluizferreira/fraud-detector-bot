# log_analyzer.py - Módulo para analisar logs e classificar fraudes via LLM (Gemini)

import json
import os
import re
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv
from config import FRAUD_PATTERNS, GEMINI_MODEL, PROCESSED_LOGS_FILE

# Carrega variáveis do .env
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError("❌ GEMINI_API_KEY não encontrada. Verifique seu arquivo .env")
genai.configure(api_key=api_key)
model = genai.GenerativeModel(GEMINI_MODEL)


def _heuristic_pre_check(log_entry: dict) -> Optional[str]:
    hints = []
    event_type = log_entry.get("event_type", "")
    status = log_entry.get("status", "")
    amount = log_entry.get("amount", 0) or 0
    details = log_entry.get("details", {})
    resource = details.get("resource", "")

    if event_type == "login_failed" and status == "failed":
        attempts = details.get("failed_attempts", 1)
        countries = details.get("countries", [])
        if attempts >= FRAUD_PATTERNS["max_failed_logins"]:
            hints.append(f"Múltiplas tentativas de login falhas ({attempts} tentativas) de {len(countries)} países diferentes.")

    if event_type == "transaction" and amount > FRAUD_PATTERNS["high_value_transaction"]:
        avg = details.get("user_avg_transaction", amount)
        ratio = amount / avg if avg > 0 else 1
        hints.append(f"Transação de alto valor: R$ {amount:.2f} (média do usuário: R$ {avg:.2f}, ratio: {ratio:.1f}x).")

    if event_type == "transaction":
        try:
            from datetime import datetime
            ts = log_entry.get("timestamp", "")
            hour = datetime.fromisoformat(ts).hour
            if hour in FRAUD_PATTERNS["suspicious_hours"]:
                hints.append(f"Transação realizada às {hour}h (horário suspeito: madrugada).")
        except Exception:
            pass

    if resource in FRAUD_PATTERNS["sensitive_resources"] and status == "denied":
        attempts = details.get("attempts", 1)
        hints.append(f"Tentativa de acesso a recurso restrito '{resource}' ({attempts} tentativas), acesso negado.")

    return " | ".join(hints) if hints else None


def classify_log_with_llm(log_entry: dict) -> dict:
    """Usa o Gemini para classificar uma entrada de log como NORMAL ou SUSPEITO/FRAUDE."""
    log_json = json.dumps(log_entry, ensure_ascii=False, indent=2, default=str)
    hint = _heuristic_pre_check(log_entry)
    hint_text = f"\n\nDica heurística detectada: {hint}" if hint else ""

    prompt = f"""Analise a seguinte entrada de log de sistema e classifique-a como exatamente 'NORMAL' ou 'SUSPEITO/FRAUDE'.
Forneça uma justificativa concisa (1-2 frases) para sua classificação.

Entrada de Log:
{log_json}{hint_text}

Responda SOMENTE no seguinte formato JSON (sem markdown, sem blocos de código):
{{
  "classification": "NORMAL" ou "SUSPEITO/FRAUDE",
  "justification": "sua justificativa aqui"
}}"""

    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    raw_text = response.text.strip()

    try:
        clean = re.sub(r"```(?:json)?", "", raw_text).strip().rstrip("```").strip()
        result = json.loads(clean)
        return {
            "classification": result.get("classification", "INDETERMINADO"),
            "justification": result.get("justification", raw_text),
        }
    except json.JSONDecodeError:
        classification = "SUSPEITO/FRAUDE" if "SUSPEITO" in raw_text.upper() or "FRAUDE" in raw_text.upper() else "NORMAL"
        return {"classification": classification, "justification": raw_text}


def analyze_logs(logs: list[dict], verbose: bool = True) -> list[dict]:
    """Analisa uma lista de logs, dispara alertas para suspeitos e salva os resultados."""
    from alert_manager import send_alert

    results = []
    total = len(logs)
    print(f"\n🔍 Analisando {total} entradas de log...\n")

    for i, log in enumerate(logs, 1):
        if verbose:
            print(f"  [{i:>{len(str(total))}}/{total}] {log.get('event_type', 'unknown')} | user: {log.get('user_id', '?')} ...", end=" ", flush=True)

        classification_result = classify_log_with_llm(log)
        entry = {**log, "analysis": classification_result}
        results.append(entry)

        is_suspicious = "SUSPEITO" in classification_result["classification"]

        if verbose:
            icon = "🚨" if is_suspicious else "✅"
            print(f"{icon} {classification_result['classification']}")

        if is_suspicious:
            send_alert(log, classification_result["justification"])

    # Salva logs processados para o dashboard
    _save_processed_logs(results)

    return results


def _save_processed_logs(logs: list[dict]) -> None:
    """Persiste os logs processados para uso no dashboard."""
    os.makedirs(os.path.dirname(PROCESSED_LOGS_FILE), exist_ok=True)

    existing = []
    if os.path.exists(PROCESSED_LOGS_FILE):
        try:
            with open(PROCESSED_LOGS_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = []

    # Evita duplicatas por timestamp + user_id
    existing_keys = {(e.get("timestamp"), e.get("user_id")) for e in existing}
    new_logs = [l for l in logs if (l.get("timestamp"), l.get("user_id")) not in existing_keys]

    combined = existing + new_logs
    with open(PROCESSED_LOGS_FILE, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2, default=str)

    if new_logs:
        print(f"\n💾 {len(new_logs)} novo(s) log(s) salvo(s) em '{PROCESSED_LOGS_FILE}'")


def generate_report(analyzed_logs: list[dict]) -> dict:
    suspicious = [l for l in analyzed_logs if "SUSPEITO" in l.get("analysis", {}).get("classification", "")]
    normal = [l for l in analyzed_logs if "SUSPEITO" not in l.get("analysis", {}).get("classification", "")]
    return {
        "summary": {
            "total_analyzed": len(analyzed_logs),
            "total_suspicious": len(suspicious),
            "total_normal": len(normal),
            "fraud_rate_percent": round(len(suspicious) / len(analyzed_logs) * 100, 1) if analyzed_logs else 0,
        },
        "suspicious_events": suspicious,
    }


def save_report(report: dict, filepath: str) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n📄 Relatório salvo em '{filepath}'")


def print_report_summary(report: dict) -> None:
    summary = report["summary"]
    suspicious = report["suspicious_events"]

    print("\n" + "=" * 60)
    print("📊  RELATÓRIO DE DETECÇÃO DE FRAUDES")
    print("=" * 60)
    print(f"  Total analisado   : {summary['total_analyzed']}")
    print(f"  Eventos normais   : {summary['total_normal']}")
    print(f"  Eventos suspeitos : {summary['total_suspicious']}")
    print(f"  Taxa de fraude    : {summary['fraud_rate_percent']}%")
    print("=" * 60)

    if not suspicious:
        print("\n✅ Nenhuma atividade suspeita detectada.")
        return

    print(f"\n🚨 ATIVIDADES SUSPEITAS/FRAUDE ({len(suspicious)} evento(s)):\n")
    for i, event in enumerate(suspicious, 1):
        analysis = event.get("analysis", {})
        print(f"  [{i}] {'─' * 50}")
        print(f"      Timestamp  : {event.get('timestamp', 'N/A')}")
        print(f"      Usuário    : {event.get('user_id', 'N/A')}")
        print(f"      Evento     : {event.get('event_type', 'N/A')}")
        print(f"      IP Origem  : {event.get('source_ip', 'N/A')}")
        if event.get("amount"):
            print(f"      Valor      : R$ {event['amount']:.2f}")
        print(f"      Status     : {event.get('status', 'N/A')}")
        print(f"      Detalhes   : {json.dumps(event.get('details', {}), ensure_ascii=False)}")
        print(f"      ⚠ Motivo  : {analysis.get('justification', 'N/A')}")
        print()
