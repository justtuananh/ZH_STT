

# from isort import file
from scipy.io import wavfile
import os
from chinese import transcribe_audio_to_string
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def checkDuration_Trans(fileName):
    subprocess.call("cd", shell=True)
    
    input_path = os.path.join(ROOT_DIR, fileName)
    output_path = os.path.join(ROOT_DIR, "output.wav")

    command = f'ffmpeg -i "{input_path}" -af "sample_rates=16000" -f wav "{output_path}"'
    print(f"kiet ->>> {command}")
    subprocess.call(command, shell=True)
    
    store_path = os.path.join(ROOT_DIR, "store", fileName)
    subprocess.call(f"move /Y \"{input_path}\" \"{store_path}\"", shell=True)

    time.sleep(1)
    sample_rate, data = wavfile.read(output_path)
    len_data = len(data)  # holds length of the numpy array
    t = len_data / sample_rate 
    print(t, sample_rate)

    if t > 15:
        try:
            return audioTimeSlicer(output_path)
        except Exception as e:
            print(e)
            return False
    else:
        trans = transcribe_audio_to_string(output_path)
        command = f"del /Q /F \"{output_path}\""
        subprocess.call(command, shell=True)
        return trans
        
import subprocess
import time
import os

def audioTimeSlicer(fileName):
    folderName = fileName + time.strftime("%Y%m%d_%H%M%S")

    command = f"mkdir {folderName}; mv {fileName} {folderName}"

    print(f"folder name ->>> {folderName}")

    subprocess.call(command, shell=True)


    # command = f'ffmpeg -i {fileName} -ar 16000 output.wav'
    # subprocess.call(command, shell=True)

    # ffmpeg -i 1.wav -f segment -segment_time 15 -c copy %03d.wav
    command = f'ffmpeg -i {folderName}/output.wav -f segment -segment_time 8 -c copy {folderName}/%03d.wav'
    
    subprocess.call(command, shell=True)

    print(f"kiet ->>> {command}")



    files = []
    for filename in os.listdir(f'{folderName}'):
        if filename.endswith(".wav") and filename !="output.wav" and filename != fileName:
            files.append(filename)

    files.sort()
    print(f"this is forder  ----- > {folderName}")
    print(files)

    results = []
    for filename in files:
        res = transcribe_audio_to_string(f"{folderName}/{filename}")
        results.append(res)

    transcript = ". ".join(results)

    #delete folder of slice 

    command = f"rm -r -f {folderName}"
    subprocess.call(command, shell=True)

    return transcript
    

# audioTimeSlicer(fname)

