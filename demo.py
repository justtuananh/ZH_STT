#! /usr/bin/env python3
import webbrowser
import sys
import argparse
from os.path import join, realpath
from flask import Flask, render_template, jsonify, request
from flask_sock import Sock
from model import predict_beamSearch


sys.path.append(realpath(join(realpath(__file__), '..', '..')))

from DemoRealTime import SpeechRecognitionEngine,Listener
from Happy import CheckMic, script_header

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)



app = Flask(__name__)

global asr_engine
global loop4k 


@app.route("/realtime")
def index():
    Listener().stop()
    return render_template('index.html')

# @app.route("/")
# def index():
#     Listener().stop()
#     return render_template('home.html')

@app.route("/start_asr")
def start():
    action = DemoAction()
    asr_engine.run(action)
    return jsonify("speechrecognition start success!")

import os 
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


global loop 
@app.route("/loop")
def checkloop():
    global loop
    temp = request.args.get("income")
    print(temp)
    if(temp == "done"):
        loop = True
    
    return {"result":"done"}





@app.route("/get_audio")
def get_audio():
    if(active):
        with open(ROOT_DIR +'/help/Sad', 'r') as f:
            transcript = f.read()
            Listener().stop()
    else:
        with open(ROOT_DIR + '/transcript.txt', 'r') as f:
            transcript = f.read()
                
    return jsonify(transcript)


@app.route('/receive')
def receiveData():
    audio_bytes = request.form["data"]
    print(audio_bytes[:20])
    # with open("audio.wav","wb") as f: 
    #     f.write(audio_bytes)


@app.route("/upload", methods =['GET'])
def loadUpload():
    return render_template("upload1.html", audio_path=None)


from static.upload.F2sttUpload import checkDuration_Trans


@app.route('/upload', methods=['POST'])
def predic_upload():
    print('upload file')
    print(request)
    if request.method == 'POST':
        _file = request.files['audiok']
        if _file.filename == '':
            return index()
        print('\n\nfile uploaded:',_file)
        _file.save(os.path.join(app.root_path, 'static', 'upload', _file.filename))
        print('Write file success!')
        
        audioPath = f"/static/upload/{_file.filename}"
        print(audioPath)

        ### voice2text write here
        trans = checkDuration_Trans(_file.filename)

        return render_template('uploadVoice.html',audio_path=audioPath, question = trans)



@app.route('/listen')
def echo(sock):
    while True:
        data = sock.receive()
        
        if(data):
            filename = 0
            filepath = f"{ROOT_DIR}/static/record/{filename}.wav" 
    
            with open(filepath, "wb") as f:
                print(data[:30]+ data[-30:])
                f.write(data)

            filename += 1

            transcript = predict_beamSearch(filepath)

            #subprocess.call(f"rm {ROOT_DIR}/{filepath}", shell=True)
            if(transcript):
                sock.send(transcript)


class DemoAction:

    def __init__(self):
        self.asr_results = ""
        self.current_beam = ""
    
    def __call__(self, x):
        results, current_context_length = x
        self.current_beam = results
        trascript = " ".join(self.asr_results.split() + results.split())
        print(trascript)
        if(active):
            self.save_transcript(trascript)
            if current_context_length > 4:
                self.asr_results = trascript

        else:
            with open(ROOT_DIR + '/help/Sad', 'r') as f:
                self.save_transcript(f.read())
                
            # self.save_doc(trascript)

    def save_transcript(self, transcript):
        with open(ROOT_DIR + "/transcript.txt", 'w+') as f:
            f.write(transcript)
            # f.close()
            
active = False

def main():
    global asr_engine
    active = CheckMic()
    if(active):
        parser = argparse.ArgumentParser(description="demoing the speech recognition engine")
        asr_engine = SpeechRecognitionEngine()
        webbrowser.open_new('http://127.0.0.1:3000/upload')
        app.run(port=3000)
    





if __name__ == "__main__":
    script_header()
    main()

