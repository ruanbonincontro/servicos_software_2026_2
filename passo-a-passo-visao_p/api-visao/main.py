"""
Backend (api-visao) — remoção de fundo de imagem com rembg.

Segue o mesmo padrão do par api-visao / gradio-visao do repositório modelo
da disciplina: recebe a imagem via REST (multipart/form-data) na rota
/analisar e devolve o resultado processado.

Modelo: u2netp (rembg), um modelo de terceiros pronto, leve (~4,6 MB),
baixado automaticamente do GitHub na primeira execução e cacheado no
container. Não precisa de treino nem de hospedar pesos grandes.
"""

import io

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response
from PIL import Image, UnidentifiedImageError
from rembg import new_session, remove

app = FastAPI(title="api-visao — Remoção de Fundo")

# Carrega o modelo uma única vez, na subida do container.
print("Carregando modelo de remoção de fundo (u2netp)...")
session = new_session("u2netp")
print("Modelo pronto.")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analisar")
async def analisar_imagem(file: UploadFile = File(...)):
    conteudo = await file.read()
    if not conteudo:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")

    try:
        Image.open(io.BytesIO(conteudo)).verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=400, detail="O arquivo enviado não é uma imagem válida.")

    imagem_sem_fundo = remove(conteudo, session=session)  # bytes PNG com canal alfa

    return Response(content=imagem_sem_fundo, media_type="image/png")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8081)
