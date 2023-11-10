from fastapi import FastAPI, Body, Request, Form,UploadFile,File,Response,Header
from pathlib import Path
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import uvicorn
from model import predict_greedy,predict_beamSearch
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def getMainPage(request: Request):
    voicefile = ""
    return templates.TemplateResponse("voice2textV2.html", {"request": request, "voicefile":voicefile})


@app.post('/voice2text')
async def receiveData(request: Request,file: UploadFile= File(...)):
    start=datetime.now()
    audio_bytes = file.file.read()
    with open("audio.wav","wb") as f: 
        f.write(audio_bytes)
    #call voice2text to convert voice recorded to text
    # question = predict_greedy("audio.wav")
    question = predict_beamSearch("audio.wav")
    print (f"Time voice2text run: {datetime.now()-start}")

    return question


if __name__ == "__main__":
    uvicorn.run(app,port=3000) 