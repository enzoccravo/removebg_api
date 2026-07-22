import os
import gc
import io
import base64
import asyncio
from fastapi import FastAPI, Request, Response
import uvicorn
from PIL import Image

# Configurações anti-ram
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

print(">> STARTING !!!!!!!!!!!!", flush=True)
from rembg import new_session, remove
my_session = new_session("u2netp")
print(">> AI LOADED !!!!!!!!!!!!", flush=True)

app = FastAPI()

@app.get("/")
def root():
    return {"status": "server on"}

@app.post("/remove-bg")
async def remove_bg(request: Request):
    try:
        print("[1] Recebendo imagem...", flush=True)
        content = await request.body()
        
        print("[2] Redimensionando para 600x600...", flush=True)
        img = Image.open(io.BytesIO(content))
        img.thumbnail((600, 600))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        small_content = img_byte_arr.getvalue()
        
        print("[3] Limpando rastros de RAM...", flush=True)
        del img
        del content
        gc.collect()

        print("[4] Executando IA (sem carregar nada, ja esta na memoria!)...", flush=True)
        output_image = await asyncio.to_thread(remove, small_content, session=my_session)
        
        print("[5] Sucesso! Devolvendo imagem...", flush=True)
        encoded_image = base64.b64encode(output_image).decode('utf-8')
        
        # AQUI ESTAVA O BUG! Retornando como texto puro (sem aspas do JSON)
        return Response(content=encoded_image, media_type="text/plain")
        
    except Exception as e:
        print(f"[ERRO FATAL] {str(e)}", flush=True)
        return Response(content=str(e), status_code=500)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
