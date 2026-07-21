import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["U2NET_HOME"] = "/tmp/.u2net"

from fastapi import FastAPI, Request, Response
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
    from rembg import remove, new_session
    from PIL import Image
    
    global my_session
    
    content = await request.body()
    
    img = Image.open(io.BytesIO(content))
    img.thumbnail((800, 800))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    small_content = img_byte_arr.getvalue()
    
    del img
    del content
    gc.collect()

    if my_session is None:
        print("Carregando o modelo de IA u2netp...")
        my_session = new_session("u2netp")
        
    output_image = remove(small_content, session=my_session)
    
    encoded_image = base64.b64encode(output_image).decode('utf-8')
    return encoded_image

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
