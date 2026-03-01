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

## Implantação na AWS (Próximos Passos)

Para levar o `Fraud Detector Bot` para um ambiente de produção escalável e robusto, podemos implantá-lo na Amazon Web Services (AWS) utilizando os seguintes serviços:

### 1. Armazenamento de Logs no Amazon S3

Configure um bucket S3 para armazenar seus logs de atividade. O S3 oferece alta durabilidade e escalabilidade para seus dados.

*   **Crie um Bucket S3**: Crie um novo bucket S3 na sua região AWS preferida. Ex: `meu-bucket-de-logs-fraude`.
*   **Envio de Logs**: Configure suas aplicações para enviar logs diretamente para este bucket S3. Isso pode ser feito via SDKs da AWS, ferramentas de log como Fluentd/Logstash com plugins S3, ou até mesmo via AWS Kinesis Firehose.

### 2. Processamento de Logs com AWS Lambda

Utilize uma função AWS Lambda para processar os logs assim que eles chegam ao S3. A Lambda é um serviço de computação serverless que executa seu código em resposta a eventos.

*   **Crie uma Função Lambda**: Crie uma nova função Lambda em Python (runtime 3.9+).
*   **Código da Lambda**: Adapte o `log_analyzer.py` e `alert_manager.py` para serem executados dentro da Lambda. A função Lambda será acionada por eventos do S3.
    *   **Trigger S3**: Configure um trigger no seu bucket S3 para que a função Lambda seja invocada sempre que um novo objeto (log) for criado no bucket.
    *   **Variáveis de Ambiente**: Configure as chaves de API (ex: `GEMINI_API_KEY`) e a `WEBHOOK_URL` como variáveis de ambiente na função Lambda.
    *   **Dependências**: Empacote as dependências Python (`requirements.txt`) em um arquivo `.zip` ou use camadas Lambda (Lambda Layers) para incluí-las na sua função.
*   **Permissões IAM**: A role IAM da sua função Lambda precisará de permissões para:
    *   Ler objetos do bucket S3 (`s3:GetObject`).
    *   Escrever logs no CloudWatch (`logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`).
    *   Acessar a API do Gemini (se aplicável, via Secrets Manager ou variáveis de ambiente).

### 3. Geração de Alertas com Amazon CloudWatch

O CloudWatch é o serviço de monitoramento e observabilidade da AWS. Ele pode ser usado para monitorar a execução da sua Lambda e gerar alertas.

*   **Métricas da Lambda**: O CloudWatch automaticamente coleta métricas da sua função Lambda (invocações, erros, duração).
*   **Logs da Lambda**: Os logs gerados pela sua função Lambda (incluindo as detecções de fraude) serão enviados para o CloudWatch Logs.
*   **Filtros de Métrica**: Crie filtros de métrica no CloudWatch Logs para identificar padrões específicos, como o número de logs classificados como `SUSPEITO/FRAUDE`.
    *   Exemplo: Um filtro que conta ocorrências da string "Classificação: SUSPEITO/FRAUDE" nos logs da Lambda.
*   **Alarmes CloudWatch**: Crie alarmes baseados nestas métricas filtradas.
    *   **Configuração do Alarme**: Se o número de eventos `SUSPEITO/FRAUDE` exceder um determinado limite em um período de tempo (ex: 5 fraudes em 5 minutos), o alarme é disparado.
    *   **Ações do Alarme**: Configure o alarme para enviar notificações via Amazon SNS (Simple Notification Service). O SNS pode então retransmitir essas notificações para diversos endpoints, incluindo e-mail, SMS, ou até mesmo um webhook HTTP (integrando-se ao seu `alert_manager.py` se ele for exposto via API Gateway, ou usando um serviço como o Zapier/IFTTT para converter SNS para webhook).

### Arquitetura Simplificada

```
[Sua Aplicação] --> [S3 Bucket (Logs)] --(Evento: Novo Objeto)--> [AWS Lambda (Fraud Detector Bot)]
                                                                      |
                                                                      +--> [CloudWatch Logs]
                                                                      |
                                                                      +--> [CloudWatch Metrics]
                                                                      |
                                                                      +--> [Amazon SNS (para Alertas)] --(Webhook/Email/SMS)--> [Administrador/Sistema de Alerta]
```

### Ferramentas de Automação

Considere usar ferramentas como AWS CLI, AWS CloudFormation, ou Terraform para automatizar a criação e configuração desses recursos na AWS, garantindo consistência e reprodutibilidade.

---
