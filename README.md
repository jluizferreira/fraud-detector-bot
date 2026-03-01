# 🔐 Fraud Detector Bot

Bot de análise de logs suspeitos e detecção de fraude usando IA (Claude da Anthropic).

## Visão Geral

Este bot processa logs de atividades de sistemas, identifica padrões suspeitos via análise heurística e classifica cada evento como `NORMAL` ou `SUSPEITO/FRAUDE` usando o modelo de linguagem Claude.

## Estrutura do Projeto

```
fraud_detector_bot/
├── main.py             # Ponto de entrada (CLI)
├── log_generator.py    # Geração de logs simulados
├── log_analyzer.py     # Análise e classificação via LLM
├── config.py           # Configurações e parâmetros
├── requirements.txt    # Dependências Python
└── README.md           # Esta documentação
```

## Instalação

```bash
# Clone ou baixe o projeto
cd fraud_detector_bot

# Instale as dependências
pip install -r requirements.txt

# Configure sua chave da API Gemini (obtenha gratuitamente em aistudio.google.com/apikey)
# Mac/Linux:
export GEMINI_API_KEY="sua-chave-aqui"

# Windows (PowerShell):
$env:GEMINI_API_KEY="sua-chave-aqui"
```

## Uso

### 1. Gerar logs simulados

```bash
# Gera 50 logs (padrão) com ~25% de eventos suspeitos
python main.py --generate-logs

# Gera 100 logs
python main.py --generate-logs 100

# Gera 200 logs com 40% suspeitos em arquivo customizado
python main.py --generate-logs 200 --suspicious-ratio 0.4 --output meus_logs.json
```

### 2. Analisar logs

```bash
# Analisa o arquivo padrão (simulated_logs.json)
python main.py --analyze-logs

# Analisa um arquivo específico
python main.py --analyze-logs meus_logs.json

# Analisa apenas os primeiros 10 logs (útil para testes)
python main.py --analyze-logs --limit 10

# Salva relatório em local customizado
python main.py --analyze-logs meus_logs.json --report-output meu_relatorio.json
```

### 3. Exibir relatório

```bash
# Exibe o relatório padrão (fraud_report.json)
python main.py --report

# Exibe um relatório específico
python main.py --report meu_relatorio.json
```

### Fluxo completo (exemplo rápido)

```bash
# Passo 1: Gerar 30 logs
python main.py --generate-logs 30

# Passo 2: Analisar (limitado a 10 para economizar chamadas de API)
python main.py --analyze-logs --limit 10

# Passo 3: Ver relatório
python main.py --report
```

## Tipos de Eventos Detectados

| Tipo | Descrição |
|------|-----------|
| **Brute Force** | Múltiplas tentativas de login falhas de IPs/países diferentes |
| **Alto Valor** | Transações acima de R$ 10.000 com valor muito acima da média do usuário |
| **Horário Suspeito** | Transações realizadas entre 0h e 5h da manhã |
| **Acesso Não Autorizado** | Tentativas de acesso a recursos restritos (`/admin`, `/config`, etc.) |

## Configuração

Edite `config.py` para ajustar os parâmetros de detecção:

```python
FRAUD_PATTERNS = {
    "max_failed_logins": 3,          # Tentativas antes de ser suspeito
    "high_value_transaction": 10000,  # Valor mínimo suspeito (R$)
    "suspicious_hours": list(range(0, 6)),  # Horas suspeitas
    "sensitive_resources": ["/admin", "/config", "/users/all"],
}
```

## Como Funciona

1. **Geração**: `log_generator.py` usa a biblioteca `Faker` para criar logs realistas com eventos normais e suspeitos misturados.

2. **Análise Heurística**: Antes de chamar o LLM, `log_analyzer.py` faz uma verificação rápida baseada em regras para identificar padrões óbvios e gerar dicas de contexto.

3. **Classificação com LLM**: Cada log (com as dicas heurísticas) é enviado ao Claude via API. O modelo retorna `NORMAL` ou `SUSPEITO/FRAUDE` com uma justificativa.

4. **Relatório**: Os resultados são agregados e exibidos com estatísticas e detalhes de cada evento suspeito.

## Dependências

- `google-generativeai` — SDK oficial do Google para acessar o Gemini
- `faker` — Geração de dados sintéticos realistas

## Requisitos

- Python 3.9+
- Chave de API Gemini gratuita (`GEMINI_API_KEY`) — obtenha em **aistudio.google.com/apikey**
