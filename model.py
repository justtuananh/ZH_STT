import torch
import torchaudio
from transformers import Wav2Vec2FeatureExtractor
from custom import Wav2Vec2WordpieceTokenizer
from pyctcdecode import Alphabet,BeamSearchDecoderCTC,LanguageModel, alphabet, decoder
import kenlm


from pathlib import Path
path_root = Path(__file__).parents[0]

lm_file =str(path_root)+'/4gram/lm.binary'
lm_model = kenlm.Model(lm_file)




device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = torch.jit.load(str(path_root)+'/model_asr1.pth',map_location=device)
model.to(device)
model.eval()

x = torch.zeros([1, 4000]).to(device)
test_pass=model(x)
print('pass')
# print(model.mods.encoder)
extractor = Wav2Vec2FeatureExtractor(padding_side="right",do_normalize=True,feature_size=1,padding_value=0.0,return_attention_mask=False,sampling_rate=16000)
def get_decoder_ngram_model(tokenizer):
    vocab_dict = tokenizer.get_vocab()
    sort_vocab = sorted((value,key) for (key,value) in vocab_dict.items())
    vocab =[x[1] for x in sort_vocab]#[:-2]
    vocab_list = vocab
    vocab_list[tokenizer.pad_token_id] =""
    vocab_list[tokenizer.unk_token_id] =""
    
    vocab_list[tokenizer.word_delimiter_token_id]= " "
    alphabet = Alphabet.build_alphabet(vocab_list,ctc_token_idx=tokenizer.pad_token_id)
    
    decoder= BeamSearchDecoderCTC(alphabet,language_model=LanguageModel(lm_model))
    return decoder
# 
# audio, sample_rate = torchaudio.load('./quangnam.wav')
# input = extractor(audio[0].to(torch.device('cuda')),sampling_rate=16000,return_tensors="pt").input_values
# input_lens = torch.ones(input.shape[0])
tokenizer = Wav2Vec2WordpieceTokenizer(str(path_root)+'/vocab.json')
# # print(tokenizer.get_vocab())
ngram_lm_model = get_decoder_ngram_model(tokenizer)
# print((input.to(torch.device('cuda'))))
# output = model(input.to(torch.device('cuda')),input_lens.to(torch.device('cuda')))
# beam_search_output = ngram_lm_model.decode(output[0].cpu().detach().numpy(), beam_width=100)
# print(beam_search_output)
# 






def predict_greedy(file):
    audio, sample_rate = torchaudio.load(file)
    input = extractor(audio[0],sampling_rate=16000,return_tensors="pt").input_values
    output = model(input.to(device))
    result_str=tokenizer.decode(torch.argmax(output,dim=-1)[0])
    return result_str
    
    
def predict_beamSearch(file):
    audio, sample_rate = torchaudio.load(file)
    input = extractor(audio[0],sampling_rate=16000,return_tensors="pt").input_values
    output = model(input.to(device))
    beam_search_output = ngram_lm_model.decode(output[0].cpu().detach().numpy(), beam_width=100)
    return beam_search_output

import io
def predict_beamSearch_io(waveform):
    file = io.BytesIO(waveform)
    audio, sample_rate = torchaudio.load(file)
    input = extractor(audio[0],sampling_rate=16000,return_tensors="pt").input_values
    output = model(input.to(device))
    beam_search_output = ngram_lm_model.decode(output[0].cpu().detach().numpy(), beam_width=100)
    return beam_search_output

def predict_greedy_io(waveform):
    file = io.BytesIO(waveform)
    audio, sample_rate = torchaudio.load(file)
    input = extractor(audio[0],sampling_rate=16000,return_tensors="pt").input_values
    output = model(input.to(device))
    result_str=tokenizer.decode(torch.argmax(output,dim=-1)[0])
    return result_str

    
if __name__=="__main__":
    asr=predict_beamSearch('/home/justtuananh/AI4TUAN/ASR_BETA/duysua.wav')
    print(asr)
