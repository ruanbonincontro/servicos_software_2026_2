"""
Frontend (gradio-visao) — interface para remoção de fundo de imagem.

Envia a foto para o backend (api-visao) via REST e mostra o resultado
(imagem com fundo removido, PNG com transparência).
"""

import io

import gradio as gr
import requests
from PIL import Image

API_URL = "http://api-visao:8081/analisar"


def remover_fundo(imagem_path):
    if imagem_path is None:
        return None, "Nenhuma imagem enviada."

    with open(imagem_path, "rb") as f:
        files = {"file": f}
        try:
            response = requests.post(API_URL, files=files, timeout=60)
        except Exception as e:
            return None, f"Erro de comunicação com o backend: {e}"

    if response.status_code != 200:
        detalhe = response.text
        return None, f"Erro no servidor ({response.status_code}): {detalhe}"

    imagem_resultado = Image.open(io.BytesIO(response.content))
    return imagem_resultado, "Fundo removido com sucesso."


demo = gr.Interface(
    fn=remover_fundo,
    inputs=gr.Image(type="filepath", label="Envie uma imagem"),
    outputs=[
        gr.Image(type="pil", label="Imagem sem fundo", image_mode="RGBA"),
        gr.Textbox(label="Status"),
    ],
    title="🖼️ Removedor de Fundo de Imagem",
    description="Envie uma foto e o backend (rembg) remove o fundo automaticamente.",
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7861)
