import os 

folderName = "test"
files = []
for filename in os.listdir(f'./{folderName}'):
    if filename.endswith(".wav") and filename !="output.wav" :
        files.append(filename)




print(files)