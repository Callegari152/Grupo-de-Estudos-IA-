import statistics
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
MODEL = "gemini-3.5-flash-lite"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def obter_temperatura_servidor(datacenter: str) -> dict:
    """Retorna a temperatura atual em graus Celsius de um datacenter (sp-01, rs-02 ou rj-03)."""
    tabela = {"sp-01": 24.5, "rs-02": 21.0, "rj-03": 27.8}
    return {"datacenter": datacenter, "celsius": tabela[datacenter]}


def verificar_status_banco(cluster: str) -> dict:
    """Retorna o status operacional de um cluster de banco de dados (prod, homolog ou analytics)."""
    # TODO: retorne {"cluster": cluster, "status": ...} com prod="saudavel", homolog="degradado", analytics="offline"
    return {"cluster": cluster, "status": {"prod": "saudavel", "homolog": "degradado", "analytics": "offline"}[cluster]}


def calcular_desvio_padrao(valores: list[float]) -> float:
    """Calcula o desvio padrao amostral de uma lista com pelo menos 2 numeros."""
    # TODO: use statistics.stdev e arredonde para 2 casas decimais
    return round(statistics.stdev(valores), 2)  
    


def validar_formato_documento(cnpj: str) -> dict:
    """Confere apenas o FORMATO de um CNPJ (14 digitos, com ou sem pontuacao); nao consulta a Receita."""
    # TODO: remova pontuacao, verifique se restam exatamente 14 digitos e retorne {"cnpj": cnpj, "formato_valido": bool}
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
    return {"cnpj": cnpj, "formato_valido": len(cnpj_limpo) == 14}


FERRAMENTAS = {
    "obter_temperatura_servidor": obter_temperatura_servidor,
    "verificar_status_banco": verificar_status_banco,
    "calcular_desvio_padrao": calcular_desvio_padrao,
    "validar_formato_documento": validar_formato_documento,
}


def responder(pergunta: str) -> tuple[str | None, str | None]:
    config = types.GenerateContentConfig(
        tools=list(FERRAMENTAS.values()),
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    contents = [types.Content(role="user", parts=[types.Part(text=pergunta)])]

    response = client.models.generate_content(model=MODEL, contents=contents, config=config)
    if not response.function_calls:
        return response.text, None

    contents.append(response.candidates[0].content)
    primeira_chamada = response.function_calls[0].name
    partes_resposta = []
    for chamada in response.function_calls:
        funcao = FERRAMENTAS.get(chamada.name)
        resultado = funcao(**chamada.args) if funcao else None
        partes_resposta.append(
            types.Part.from_function_response(
                name=chamada.name,
                response={"result": resultado},
            )
        )

    contents.append(types.Content(role="user", parts=partes_resposta))
    response_final = client.models.generate_content(model=MODEL, contents=contents, config=config)
    return response_final.text, primeira_chamada


# (prompt, ferramenta_esperada ou None quando NAO deve chamar ferramenta)
BATERIA = [
    ("Qual a temperatura do datacenter rs-02?", "obter_temperatura_servidor"),
    ("O cluster analytics esta funcionando?", "verificar_status_banco"),
    ("Qual o desvio padrao de 10, 12, 9, 15 e 11?", "calcular_desvio_padrao"),
    ("O CNPJ 12.345.678/0001-95 tem formato valido?", "validar_formato_documento"),
    ("Explique em duas frases o que e um cluster de banco de dados.", None),
    ("Para que serve o desvio padrao em monitoramento de servidores?", None),
]

if __name__ == "__main__":
    acertos = 0
    for pergunta, esperada in BATERIA:
        # TODO: descubra qual ferramenta o modelo chamou (ou None) e compare com "esperada".
        # Dica: adapte responder() para tambem retornar o nome da primeira chamada, se houver.
        resposta, chamada = responder(pergunta)
        print("PERGUNTA:", pergunta)
        print("CHAMADA:", chamada)
        print("ESPERADA:", esperada)
        if chamada is None:
            print("Resposta do modelo:", resposta)
        print()
        if chamada == esperada:
            print(chamada)
            acertos += 1 
        pass
    print(f"Roteamento correto: {acertos}/{len(BATERIA)}")