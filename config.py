# config.py - Configurações do bot de detecção de fraude

# Padrões de fraude para análise heurística
FRAUD_PATTERNS = {
    "max_failed_logins": 3,          # Máximo de logins falhos consecutivos
    "high_value_transaction": 10000,  # Valor em R$ considerado alto
    "suspicious_hours": list(range(0, 6)),  # Horas suspeitas (0h-5h)
    "sensitive_resources": ["/admin", "/config", "/users/all", "/export/data"],
    "max_transactions_per_hour": 10,
}

# Configuração da API Gemini
GEMINI_MODEL = "gemini-2.5-flash"
MAX_TOKENS = 500

# Configuração de logs
LOG_FILE_DEFAULT = "simulated_logs.json"
REPORT_FILE_DEFAULT = "fraud_report.json"
