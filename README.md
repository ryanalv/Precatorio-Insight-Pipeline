# Precatorio Insight Pipeline

MVP educacional de pré-análise de precatórios com FastAPI, Streamlit, SQLite e IA generativa via API OpenAI-compatible.

## Objetivo

O projeto simula uma esteira inicial de triagem de oportunidades de precatórios. Ele permite entrada manual ou upload de PDF, estrutura os dados em schemas Pydantic, valida campos mínimos, calcula um score de completude documental, aplica uma classificação comercial simulada e gera um resumo executivo com Qwen 14B ou fallback determinístico.

Este sistema não emite parecer jurídico, não aprova crédito automaticamente e não deve ser usado com dados reais sensíveis. Ele foi criado como MVP demonstrativo para portfólio, entrevistas e estudo de automação aplicada a negócios.

## Contexto de Negócio

Empresas de antecipação de precatórios precisam organizar documentos, identificar campos críticos, priorizar oportunidades e reduzir esforço manual na triagem. Este MVP mostra como IA generativa, validação de dados e automação podem apoiar essa etapa inicial sem substituir especialistas.

## Arquitetura

- `app/main.py`: aplicação FastAPI.
- `app/routes/analysis_routes.py`: endpoints de análise e histórico.
- `app/schemas.py`: contratos Pydantic de entrada e resposta.
- `app/services/pdf_extractor.py`: extração de texto de PDF com `pypdf`.
- `app/services/field_parser.py`: parsing heurístico de texto livre para dados estruturados.
- `app/services/validator.py`: validação de campos obrigatórios.
- `app/services/scorer.py`: score documental determinístico de 0 a 100.
- `app/services/classifier.py`: regras transparentes de classificação simulada.
- `app/services/llm_client.py`: integração OpenAI-compatible com Qwen.
- `app/database.py`: persistência local em SQLite.
- `frontend/streamlit_app.py`: interface simples para uso do MVP.
- `tests/`: testes unitários das regras principais.

## Configuração

Crie um arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

Preencha as variáveis:

```env
QWEN_API_KEY=
QWEN_BASE_URL=
QWEN_MODEL=qwen-14b
DATABASE_PATH=precatorio_insight.db
API_BASE_URL=http://localhost:8000
```

A chave da LLM deve ficar apenas no `.env`. O modelo é configurável porque o nome exato pode variar conforme o provedor.

## Instalação

```bash
pip install -r requirements.txt
```

## Rodar o Backend

```bash
uvicorn app.main:app --reload
```

A API ficará disponível em:

```text
http://localhost:8000
```

Documentação interativa:

```text
http://localhost:8000/docs
```

## Rodar o Streamlit

Com o backend ativo, execute:

```bash
streamlit run frontend/streamlit_app.py
```

## Endpoints

- `GET /`: status da API.
- `POST /analyze/manual`: recebe JSON com dados do precatório.
- `POST /analyze/pdf`: recebe PDF, extrai texto e analisa.
- `GET /analyses`: lista análises salvas.
- `GET /analyses/{id}`: busca uma análise específica.

## Exemplo de Entrada Manual

```json
{
  "nome_credor": "Maria Silva",
  "numero_processo": "1234567-89.2024.8.26.0053",
  "tribunal": "TJSP",
  "ente_devedor": "Estado de São Paulo",
  "valor_estimado": 185000,
  "tipo_precatorio": "Estadual",
  "natureza": "Alimentar",
  "data_prevista_pagamento": "31/12/2026",
  "status_documental": "Parcial",
  "observacoes": "Exemplo fictício para teste."
}
```

Também há um arquivo de exemplo em `sample_data/exemplo_precatorio.txt`.

## Regras de Score

- `nome_credor`: +15
- `numero_processo`: +20
- `ente_devedor`: +15
- `valor_estimado`: +20
- `natureza`: +10
- `tribunal`: +10
- `data_prevista_pagamento`: +10

## Classificação Simulada

- Score abaixo de 50 ou valor ausente: `Dados insuficientes`
- Valor estimado abaixo de R$ 50.000: `Fora do perfil simulado`
- Campos obrigatórios pendentes: `Necessita revisão documental`
- Score a partir de 75 e valor a partir de R$ 50.000: `Alta prioridade comercial`
- Score a partir de 65 e valor a partir de R$ 50.000: `Média prioridade`
- Demais casos: `Necessita revisão documental`

## Testes

```bash
pytest
```

## Segurança e Limitações do MVP

- Não armazena documentos originais enviados, apenas análise estruturada e prévia curta do texto extraído.
- Não deve receber dados reais sensíveis.
- Não substitui análise jurídica, financeira, cadastral ou documental feita por especialistas.
- A extração de campos por PDF é heurística e pode falhar em documentos digitalizados como imagem.
- A classificação é simulada e serve apenas para demonstração técnica.
- A resposta da IA pode ficar indisponível se `QWEN_API_KEY` ou `QWEN_BASE_URL` não estiverem configurados; nesse caso, o sistema usa resumo determinístico.

## Melhorias Futuras

- OCR para PDFs escaneados.
- Docker e Docker Compose.
- Autenticação e controle de acesso.
- Fila assíncrona para processamento de documentos.
- Dashboard analítico com métricas de funil.
- Regras de negócio parametrizáveis por equipe.
- Observabilidade com logs estruturados.
- Testes de integração para API e frontend.
