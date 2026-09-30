# ... importacoes, client e config copiados do 02_tool_dispatcher.py ...
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
MODEL = "gemini-3.5-flash-lite"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def dividir_metricas(numerador: float, denominador: float) -> dict:
    """Divide duas metricas e retorna a razao (por exemplo, erros por requisicao)."""
    return {"razao": numerador / denominador}


def consultar_servico_externo(servico: str) -> dict:
    """Consulta o status de um servico externo pelo nome."""
    raise ConnectionError(f"Servico '{servico}' temporariamente indisponivel")


FERRAMENTAS = {
    "dividir_metricas": dividir_metricas,
    "consultar_servico_externo": consultar_servico_externo,
}


def executar_com_seguranca(nome: str, args: dict) -> dict:
    """Executa a ferramenta e transforma qualquer excecao em um resultado estruturado."""
    try:
        # TODO: execute FERRAMENTAS[nome](**args) e retorne {"status": "sucesso", "resultado": ...}
        ...
    except KeyError:
        return {"status": "falha", "error": f"Ferramenta desconhecida: {nome}"}
    except Exception as erro:
        # TODO: retorne {"status": "falha", "error": <mensagem curta, sem traceback completo>}
        ...


PERGUNTAS = [
    "Qual a razao entre 50 erros e 0 requisicoes?",
    "O servico de pagamentos esta no ar?",
]

# TODO: para cada pergunta, rode o ciclo completo usando executar_com_seguranca no passo de execucao
# e imprima a resposta final do modelo