# config.py - Configurações do bot de detecção de fraude

# Padrões de fraude para análise heurística
FRAUD_PATTERNS = {
    "max_failed_logins": 3,
    "high_value_transaction": 10000,
    "suspicious_hours": list(range(0, 6)),
    "sensitive_resources": ["/admin", "/config", "/users/all", "/export/data"],
    "max_transactions_per_hour": 10,
}

# Configuração da API Gemini
GEMINI_MODEL = "gemini-2.5-flash"
MAX_TOKENS = 500

# Configuração de arquivos
LOG_FILE_DEFAULT = "simulated_logs.json"
REPORT_FILE_DEFAULT = "fraud_report.json"
PROCESSED_LOGS_FILE = "data/processed_logs.json"

# Configuração de alertas via Webhook
# Exemplos:
#   Discord : https://discord.com/api/webhooks/SEU_ID/SEU_TOKEN
#   Slack   : https://hooks.slack.com/services/SEU/TOKEN/AQUI
#   Genérico: qualquer endpoint HTTP que aceite POST com JSON
WEBHOOK_URL = ""  # Deixe vazio para desativar alertas

# Limite de alertas por minuto (anti-spam)
ALERT_RATE_LIMIT = 10
