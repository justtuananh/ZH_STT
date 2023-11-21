import io
import torch
import librosa
import torchaudio
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
LANG_ID = "zh-CN"
MODEL_ID = "jonatasgrosman/wav2vec2-large-xlsr-53-chinese-zh-cn"
    # Load the Wav2Vec2 processor and model
processor = Wav2Vec2Processor.from_pretrained(MODEL_ID)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID, cache_dir = "./model")
    # Function to convert speech file to array
def speech_file_to_array_fn(path):
        speech_array, sampling_rate = librosa.load(path, sr=16_000)
        return speech_array, sampling_rate
def transcribe_audio_to_string(audio_path):
    # Process the input audio file
    input, sample_rate = speech_file_to_array_fn(audio_path)
    inputs = processor(input, sampling_rate=sample_rate, return_tensors="pt", padding=True)

    # Perform inference and get predicted sentences
    with torch.no_grad():
        logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits

    predicted_ids = torch.argmax(logits, dim=-1)
    predicted_sentences = processor.batch_decode(predicted_ids)

    # Convert the list of sentences to a single string
    predicted_string = ' '.join(predicted_sentences)

    return predicted_string


def predict_greedy_io(waveform):
    file = io.BytesIO(waveform)
    input, sample_rate = speech_file_to_array_fn(file)
    inputs = processor(input, sampling_rate=sample_rate, return_tensors="pt", padding=True)
    with torch.no_grad():
        logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits

    predicted_ids = torch.argmax(logits, dim=-1)
    predicted_sentences = processor.batch_decode(predicted_ids)

    # Convert the list of sentences to a single string
    predicted_string = ' '.join(predicted_sentences)
    return predicted_sentences