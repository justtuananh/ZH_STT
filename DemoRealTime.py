from concurrent.futures import thread
import wave
import pyaudio
import threading
import time
import argparse
#from soupsieve import select
import torchaudio 
import sys
import numpy as np
import wave
import os 
from model import *


class Listener:
    def __init__(self,sample_rate = 16000,record_seconds=2):
        self.chunk = 1024
        self.sample_rate = sample_rate
        self.record_seconds = record_seconds
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  rate=self.sample_rate,
                                  channels=1,
                                  input = True,
                                  output=True,
                                #   input_device_index=6,
                                  frames_per_buffer=self.chunk)
    def listen(self,queue):
        # self.stream.start_stream()
        while True:
            data = self.stream.read(self.chunk,exception_on_overflow= True)
            queue.append(data)
            time.sleep(0.01)
    def stop(self):
        self.stream.stop_stream()
        self.stream.close() 
        self.p.terminate()  
        thread = threading.Event()
        thread.set()   
    def run(self,queue):
        thread = threading.Thread(target=self.listen,args=(queue,),daemon=True)
        thread.start()
        print('\ Speech recognition angine is now listening...')
        
class SpeechRecognitionEngine:
    def __init__(self,context_length=10):
        self.listener = Listener(sample_rate=16000)
        self.model = model
        self.featurizer = extractor
        self.audio_q = list()
        self.out_arg = None
        self.lenght_wav =None
        self.start = False
        self.context_length = context_length * 50 # multiply by 50 because each 50 from output frame is 1 second
    def save(self,waveforms,fname="audio_temp"):
        wf = wave.open(fname,"wb")
        wf.setnchannels(1)
        wf.setsampwidth(self.listener.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b"".join(waveforms))
        wf.close()
        return fname
    def predict(self,audio):
        with torch.no_grad():
            fname = self.save(audio)
            waveform,_ = torchaudio.load(fname) # don't normalize on train
            self.lenght_wav = waveform if self.lenght_wav is None else torch.cat((self.lenght_wav,waveform),dim=1)
            log_mel = extractor(self.lenght_wav[0],sampling_rate=16000,return_tensors="pt").to(device).input_values
            input_lens = torch.ones(log_mel.shape[0])
            logits = model(log_mel,input_lens)
            self.out_arg = logits[0] #if self.out_arg is None else torch.cat((self.out_arg,logits[0]),dim=0)
            # ngram_lm_model = get_decoder_ngram_model(preprocess.tokenizer)
            results = ngram_lm_model.decode(self.out_arg.cpu().detach().numpy(), beam_width=100)
            current_context_length = self.lenght_wav.shape[1] / 160000 # in secounds
            if current_context_length > 2:
                self.lenght_wav = None
                print(results)
            with open("doc.txt", 'w+') as f:
                f.write("\n"+results)
            return results,current_context_length
    def inference_loop(self,action):
        while True:     
            if len(self.audio_q) < 5 :
                #print(f"đang nghe .... {len(self.audio_q)}")
                continue
            else:
                pred_q = self.audio_q.copy()
                self.audio_q.clear()
                action(self.predict(pred_q))
            time.sleep(0.05)
            
    def run(self,action):
        self.listener.run(self.audio_q)
        thread = threading.Thread(target=self.inference_loop,args=(action,),daemon=True)
        thread.start()
    
    
        
class DemoAction:

    def __init__(self):
        self.asr_results = ""
        self.current_beam = ""

    def __call__(self, x):
        results, current_context_length = x
        self.current_beam = results
        trascript = " ".join(self.asr_results.split() + results.split())
        
        if current_context_length > 4:
            self.asr_results = trascript



if __name__ == "__main__":
     asr_engine = SpeechRecognitionEngine()
     action = DemoAction()
     
     asr_engine.run(action)
     threading.Event().wait()     
