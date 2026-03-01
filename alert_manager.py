# alert_manager.py - Sistema de alertas via webhook

import json
import time
import requests
from datetime import datetime
from config import WEBHOOK_URL, ALERT_RATE_LIMIT

# Controle de rate limiting
_alert_timestamps: list[float] = []


def _is_rate_limited() -> bool:
    """Verifica se o limite de alertas por minuto foi atingido."""
    global _alert_timestamps
    now = time.time()
    # Remove timestamps com mais de 60 segundos
    _alert_timestamps = [t for t in _alert_timestamps if now - t < 60]
    return len(_alert_timestamps) >= ALERT_RATE_LIMIT


def _format_discord_message(log_entry: dict, justification: str) -> dict:
    """Formata a mensagem no padrão embed do Discord."""
    amount_field = []
    if log_entry.get("amount"):
        amount_field = [{"name": "💰 Valor", "value": f"R$ {log_entry['amount']:.2f}", "inline": True}]

    return {
        "embeds": [{
            "title": "🚨 Alerta de Fraude Detectada",
            "color": 15158332,  # Vermelho
            "fields": [
                {"name": "👤 Usuário", "value": log_entry.get("user_id", "N/A"), "inline": True},
                {"name": "📋 Evento", "value": log_entry.get("event_type", "N/A"), "inline": True},
                {"name": "🌐 IP Origem", "value": log_entry.get("source_ip", "N/A"), "inline": True},
                {"name": "📅 Timestamp", "value": log_entry.get("timestamp", "N/A"), "inline": True},
                {"name": "⚡ Status", "value": log_entry.get("status", "N/A"), "inline": True},
                *amount_field,
                {"name": "⚠️ Justificativa", "value": justification, "inline": False},
            ],
            "footer": {"text": "Fraud Detector Bot"},
            "timestamp": datetime.utcnow().isoformat(),
        }]
    }


def _format_slack_message(log_entry: dict, justification: str) -> dict:
    """Formata a mensagem no padrão do Slack."""
    amount_text = f"\n💰 *Valor:* R$ {log_entry['amount']:.2f}" if log_entry.get("amount") else ""
    return {
        "blocks": [
            {"type": "header", "text": {"type": "plain_text", "text": "🚨 Alerta de Fraude Detectada"}},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*Usuário:* {log_entry.get('user_id', 'N/A')}\n"
                        f"*Evento:* {log_entry.get('event_type', 'N/A')}\n"
                        f"*IP:* {log_entry.get('source_ip', 'N/A')}\n"
                        f"*Timestamp:* {log_entry.get('timestamp', 'N/A')}"
                        f"{amount_text}\n"
                        f"*⚠️ Motivo:* {justification}"
                    ),
                },
            },
        ]
    }


def _format_generic_message(log_entry: dict, justification: str) -> dict:
    """Formato JSON genérico para qualquer webhook HTTP."""
    return {
        "alert_type": "FRAUD_DETECTED",
        "timestamp": datetime.utcnow().isoformat(),
        "log": log_entry,
        "justification": justification,
    }


def _detect_webhook_type(url: str) -> str:
    if "discord.com" in url:
        return "discord"
    if "hooks.slack.com" in url:
        return "slack"
    return "generic"


def send_alert(log_entry: dict, justification: str) -> bool:
    """
    Envia um alerta para o webhook configurado.
    Retorna True se enviado com sucesso, False caso contrário.
    """
    if not WEBHOOK_URL:
        return False  # Webhook não configurado, silenciosamente ignora

    if _is_rate_limited():
        print(f"  ⚠️  Rate limit atingido ({ALERT_RATE_LIMIT} alertas/min). Alerta suprimido.")
        return False

    webhook_type = _detect_webhook_type(WEBHOOK_URL)

    if webhook_type == "discord":
        payload = _format_discord_message(log_entry, justification)
    elif webhook_type == "slack":
        payload = _format_slack_message(log_entry, justification)
    else:
        payload = _format_generic_message(log_entry, justification)

    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        response.raise_for_status()
        _alert_timestamps.append(time.time())
        print(f"  📣 Alerta enviado via webhook ({webhook_type}).")
        return True
    except requests.RequestException as e:
        print(f"  ❌ Falha ao enviar alerta: {e}")
        return False
