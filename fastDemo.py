import webbrowser
import sys
import argparse
from os.path import join, realpath
# from flask import Flask, render_template, jsonify
sys.path.append(realpath(join(realpath(__file__), '..', '..')))
# from DemoRealTime import SpeechRecognitionEngine,Listener

from fastapi import FastAPI, Body, Request, Form,UploadFile,File,Response,Header, WebSocket
from fastapi.responses import HTMLResponse,RedirectResponse,JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from Happy import CheckMic,script_header

from model import predict_greedy,predict_beamSearch,predict_beamSearch_io,predict_greedy_io

global asr_engine
global loop

import os 

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# app = Flask(__name__)

# text_transcript = 

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/",response_class=HTMLResponse)
async def index(request: Request):
    
    return templates.TemplateResponse('home.html',{"request": request})

@app.get("/realtime",response_class=HTMLResponse)
async def index(request: Request):
    
    return templates.TemplateResponse('ViewRTC.html',{"request": request})

@app.get("/record",response_class=HTMLResponse)
async def Index_record(request: Request):
    
    return templates.TemplateResponse('Record.html',{"request": request})


@app.get("/upload",response_class=HTMLResponse)
async def Index_upload(request: Request):
    
    return templates.TemplateResponse('uploadFast.html',{"request": request,"audioPath":None})



@app.get("/get_audio")
async def get_audio():
    if(not CheckMic()):
        with open(ROOT_DIR +'/help/Sad', 'r') as f:
            transcript = f.read()
            Listener().stop()
        loop = False
    else:
        with open(ROOT_DIR + '/transcript.txt', 'r') as f:
            transcript = f.read()

    return JSONResponse(transcript)

from static.upload.F2sttUpload import checkDuration_Trans

@app.post("/upload")
async def predict_upload(request: Request,file: UploadFile = File(...)):
    print(file.file)

    if file.filename == '':
        return Index_upload()


    print('\n\nfile uploaded:',file.filename)

    try:
        contents = await file.read()
        with open(ROOT_DIR+"/static/upload/"+file.filename, 'wb') as f:
            f.write(contents)
        print('Write file success!')
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        await file.close()

    
    audioPath = f"/static/upload/store/{file.filename}"
    print(audioPath)
    curPath = audioPath

    ### voice2text write here
    trans = checkDuration_Trans(file.filename)

    return templates.TemplateResponse('uploadVoice.html',{"request": request, "audio_path":audioPath, "question":trans})


import time
curPath = ""
filename = 0
@app.websocket("/listen")
async def websocket_endpoint(sock: WebSocket):
    global filename
    await sock.accept()
    while True:
        try:
            data = await sock.receive_bytes()
        except Exception as ex:
            await sock.close()
        if(data):
            
            # filepath = f"./static/record/{filename}.wav" 
            # with open(filepath, "wb") as f:
            #     # print(data[:30]+ data[-30:])
            #     f.write(data)
            # filename += 1

            #transcript = predict(filepath)
            print('@@@@@')
            start_time = time.time()
            transcript = predict_greedy_io(data)
            # transcript = predict_greedy_io(data)
            print("--- %s seconds ---" % (time.time() - start_time))

            #subprocess.call(f"rm {ROOT_DIR}/{filepath}", shell=True)
            if(transcript):
                await sock.send_text(transcript)





if __name__ == "__main__":
    script_header()
    webbrowser.open_new('http://localhost:3000/')
    uvicorn.run(app,port=3000)