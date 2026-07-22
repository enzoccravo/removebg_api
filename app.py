import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

print(">> STARTING", flush=True)
from rembg import new_session, remove
my_session = new_session("u2netp")
print(">> AI LOADED", flush=True)

from fastapi import FastAPI, Request
import uvicorn
import base64
import io
import gc

app = FastAPI()
my_session = None

@app.get("/")
def root():
    return {"status": "server on"}

@app.post("/remove-bg")
async def remove_bg(request: Request):
    try:
        print("[1] Recebendo imagem...", flush=True)
        content = await request.body()
        
        print("[2] Redimensionando para 600x600...", flush=True)
        from PIL import Image
        img = Image.open(io.BytesIO(content))
        img.thumbnail((600, 600))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        small_content = img_byte_arr.getvalue()
        
        print("[3] Limpando RAM...", flush=True)
        del img
        del content
        gc.collect()

        print("[4] Executando motor da IA...", flush=True)
        output_image = await asyncio.to_thread(remove, small_content, session=my_session)
        
        print("[5] Sucesso! Devolvendo para o Android.", flush=True)
        encoded_image = base64.b64encode(output_image).decode('utf-8')
        return encoded_image
        
    except Exception as e:
        print(f"[ERRO FATAL] {str(e)}", flush=True)
        return {"error": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
