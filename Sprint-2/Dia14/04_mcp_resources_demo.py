import asyncio
import os
import sys

from dotenv import load_dotenv
from google import genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
MODEL = "gemini-3.5-flash-lite"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
PARAMS = StdioServerParameters(command=sys.executable, args=["server_demo.py"])


async def main() -> None:
    async with stdio_client(PARAMS) as (leitura, escrita):
        async with ClientSession(leitura, escrita) as sessao:
            await sessao.initialize()

            # TODO: liste os resources com sessao.list_resources() e imprima o uri e o nome de cada um
            sessao_resources = await sessao.list_resources()
            print("RESOURCES DISPONIVEIS:")
            for resource in sessao_resources.resources:
                print(f"  - {resource.uri}: {resource.name}") 

            conteudo = await sessao.read_resource("file:///docs/regras.md")
            regras = conteudo.contents[0].text
            print(regras)

            # TODO: monte um prompt do tipo "Com base nas regras abaixo, responda: posso rodar um DELETE em producao?"
            #       inserindo o texto de "regras" como contexto e envie ao Gemini (reaproveite o client da ponte)
            prompt = f"Com base nas regras abaixo, responda: posso rodar um DELETE em producao?\n\n{regras}"
            response = await client.aio.models.generate_content(model=MODEL, contents=[{"role": "user", "parts": [{"text": prompt}]}])  
            print("RESPOSTA DO GEMINI:", response.text)


if __name__ == "__main__":
    asyncio.run(main())