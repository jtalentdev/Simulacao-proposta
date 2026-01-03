from openai import OpenAI
import os

# =====================================================
# Configuração do cliente OpenAI
# =====================================================

def _get_client():
    """
    Cria o cliente OpenAI usando a variável de ambiente OPENAI_API_KEY.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY não encontrada. "
            "Configure a variável de ambiente antes de usar a IA."
        )
    return OpenAI(api_key=api_key)


# =====================================================
# Geração de textos por IA
# =====================================================

def gerar_resumo_executivo(contexto: str, tom: str) -> str:
    """
    Gera um resumo executivo com base no contexto fornecido.

    :param contexto: Texto base sobre a proposta
    :param tom: Diretriz de tom (ex: executivo, comercial, setor farmacêutico)
    :return: Texto gerado pela IA
    """
    client = _get_client()

    prompt = f"""
Você é um consultor sênior de negócios.
Escreva um RESUMO EXECUTIVO profissional, claro e objetivo,
com tom {tom}, utilizando o contexto abaixo.

Contexto:
{contexto}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você escreve textos corporativos executivos."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=500
    )

    return response.choices[0].message.content.strip()


def gerar_texto_comercial(contexto: str, tom: str) -> str:
    """
    Gera um texto comercial detalhado com base no contexto fornecido.

    :param contexto: Texto base sobre a proposta
    :param tom: Diretriz de tom (ex: executivo, comercial, setor farmacêutico)
    :return: Texto gerado pela IA
    """
    client = _get_client()

    prompt = f"""
Você é um especialista em propostas comerciais B2B.
Escreva um TEXTO COMERCIAL estruturado, persuasivo e profissional,
com tom {tom}, utilizando o contexto abaixo.

Contexto:
{contexto}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você escreve propostas comerciais profissionais."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=800
    )

    return response.choices[0].message.content.strip()
