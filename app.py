from fastapi import FastAPI, Request, Response
from rembg import remove
import uvicorn
import base64
import os

app = FastAPI()

@app.get("/")
def root():
    return {"status": "api online"}

@app.post("/remove-bg")
async def remove_bg(request: Request):
    content = await request.body()
    output_image = remove(content)
    encoded_image = base64.b64encode(output_image).decode('utf-8')
    return encoded_image 

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
