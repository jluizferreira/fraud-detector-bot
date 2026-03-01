# 🔐 Fraud Detector Bot

Bot de análise de logs suspeitos e detecção de fraude usando IA (Gemini), com sistema de alertas via webhook e dashboard interativo.

## Estrutura do Projeto

```
fraud_detector_bot/
├── main.py             # Ponto de entrada (CLI)
├── log_generator.py    # Geração de logs simulados
├── log_analyzer.py     # Análise e classificação via LLM
├── alert_manager.py    # Sistema de alertas via webhook
├── dashboard.py        # Dashboard interativo (Streamlit)
├── config.py           # Configurações e parâmetros
├── data/               # Logs processados (gerado automaticamente, não sobe no git)
├── .env                # Chaves de API (não sobe no git)
├── .env.example        # Modelo do .env
├── requirements.txt    # Dependências Python
└── README.md           # Esta documentação
```

## Instalação

```bash
pip install -r requirements.txt
```

## Configuração

Copie o `.env.example` para `.env` e preencha:

```
GEMINI_API_KEY=sua-chave-aqui   # aistudio.google.com/apikey (gratuito)
```

Para ativar alertas, edite o `config.py`:

```python
WEBHOOK_URL = "https://discord.com/api/webhooks/SEU_ID/SEU_TOKEN"
# ou
WEBHOOK_URL = "https://hooks.slack.com/services/SEU/TOKEN/AQUI"
```

## Uso

### Gerar logs simulados
```bash
python main.py --generate-logs 100
```

### Analisar logs (classifica + envia alertas + salva para o dashboard)
```bash
python main.py --analyze-logs
python main.py --analyze-logs --limit 20
```

### Ver relatório no terminal
```bash
python main.py --report
```

### Abrir dashboard interativo
```bash
python main.py --dashboard
# Acesse: http://localhost:8501
```

## Sistema de Alertas

Suporta Discord, Slack e qualquer webhook HTTP genérico. Configure `WEBHOOK_URL` no `config.py`. O rate limit padrão é de 10 alertas/minuto (configurável via `ALERT_RATE_LIMIT`).

## Dashboard

O dashboard exibe:
- Métricas gerais (total, suspeitos, taxa de fraude)
- Gráfico de distribuição por tipo de evento
- Tendência de fraudes ao longo do tempo
- Top usuários e IPs associados a fraudes
- Tabela filtrável com eventos suspeitos recentes

## Dependências

- `google-generativeai` — SDK do Gemini (IA para classificação)
- `faker` — Geração de dados simulados
- `python-dotenv` — Carregamento do `.env`
- `requests` — Envio de webhooks
- `streamlit` — Dashboard web
- `pandas` + `plotly` — Análise e gráficos
