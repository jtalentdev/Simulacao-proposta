📊 Simulador de Precificação CLT – Cost Plus

Versão 1.0 (congelada)

📌 Visão Geral

Este projeto é um aplicativo web desenvolvido em Streamlit para simulação de precificação de serviços baseados em mão de obra CLT, utilizando o modelo Cost Plus.

O sistema foi projetado para:

simular cenários comerciais

apoiar a elaboração de propostas técnicas e comerciais

garantir total transparência de custos

permitir comparação entre regimes tributários

⚠️ Importante:
Este sistema realiza simulações financeiras para formação de preço.
Ele não substitui apuração contábil ou fiscal oficial.

🧠 Modelo de Negócio (Cost Plus)

O simulador segue o modelo Cost Plus puro, onde:

100% dos custos são repassados ao contratante, incluindo:

salários

benefícios

encargos CLT

impostos

lucro da empresa

O valor da nota fiscal representa o preço final da proposta.

Não há:

custos ocultos

subsídios internos

absorção de impostos pela empresa

⚙️ Funcionalidades Principais
👥 Estrutura de Cargos

Cadastro dinâmico de cargos

Salário individual por cargo

Quantidade de colaboradores por cargo

Remoção de cargos diretamente na interface

💼 Custos CLT

Cálculo detalhado e auditável dos encargos CLT:

INSS Patronal

RAT

FGTS

FGTS adicional

13º salário

Férias

1/3 constitucional

Benefícios (ex: vale refeição)

Retorno:

custo CLT unitário

custo CLT total

detalhamento por encargo

🧾 Regimes Tributários Suportados
🔹 Simples Nacional – Anexo III (21%)

Alíquota total fixa: 21%

DAS detalhado internamente em:

IRPJ

CSLL

PIS

COFINS

CPP

ISS

📌 Os percentuais internos representam a composição do DAS, aplicada proporcionalmente sobre a alíquota total de 21%.

🔹 Lucro Real – Alíquota Efetiva (18%)

Simulação com alíquota efetiva consolidada de 18%, já considerando:

IRPJ

CSLL

PIS

COFINS

CPRB

Créditos tributários

📌 Este modelo não representa apuração fiscal oficial, mas sim uma estimativa financeira efetiva, adequada para formação de preço e propostas comerciais.

📊 Resultados Gerados
🔹 Consolidados

Custo CLT total

Impostos totais

Lucro total

Valor final da nota fiscal

🔹 Por Cargo

Custo CLT unitário

Custo CLT total

Impostos rateados por cargo

Lucro total por cargo

Lucro unitário por colaborador

Preço unitário por cargo

Preço total por cargo

🔹 Impostos Detalhados por Cargo

Visualização expandível por cargo

Rateio proporcional dos impostos

Transparência total para auditoria e proposta técnica

🤖 Geração de Conteúdo com IA

Geração automática de:

Resumo Executivo

Texto Comercial

Textos editáveis pelo usuário

Tom:

executivo

comercial

orientado ao setor farmacêutico

📄 Relatórios em PDF

Proposta Comercial

Proposta Técnica

PDFs gerados com:

logomarca

cabeçalho profissional

paginação

textos formatados

valores consolidados

🗂️ Arquitetura do Projeto
simulador-precificacao-clt/
│
├── app.py                      # Aplicação Streamlit (UI + fluxo principal)
│
├── auth/
│   └── auth.py                 # Login e autenticação simples
│
├── core/
│   ├── clt.py                  # Cálculo de custos CLT
│   ├── precificacao.py         # Lógica Cost Plus
│   ├── ia_textos.py            # Geração de textos via IA
│   ├── relatorios.py           # Geração de PDFs
│
├── assets/
│   └── logo.png                # Logomarca utilizada nos relatórios
│
├── requirements.txt            # Dependências do projeto
│
└── README.md                   # Documentação (este arquivo)

🔐 Autenticação

Login simples baseado em usuário/senha

Hash SHA-256

Controle de sessão via streamlit.session_state

Adequado para uso interno e MVP

🔑 Variáveis de Ambiente

Para funcionamento da IA, é necessário configurar:

OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx


No Streamlit Cloud, isso deve ser feito via Secrets.

⚠️ Observações Importantes

Este sistema é uma ferramenta de simulação

Não substitui:

contador

ERP

apuração fiscal oficial

Todas as alíquotas foram definidas intencionalmente e documentadas

Alterações tributárias devem ser feitas com critério e versionadas

🏷️ Versionamento

Esta versão corresponde a:

v1.0 – Versão estável
