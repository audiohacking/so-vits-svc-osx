import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import argparse
import torch
import librosa

from tqdm import tqdm
from transformers import Data2VecAudioModel, Wav2Vec2Processor


def load_audio(file: str, sr: int = 16000):
    x, sr = librosa.load(file, sr=sr)
    return x


def load_model(path, device):
    processor = Wav2Vec2Processor.from_pretrained(path)
    model = Data2VecAudioModel.from_pretrained(path)
    model.eval()
    model.to(device)
    return model, processor


def pred_vec(model, processor, wavPath, vecPath, device):
    audio = load_audio(wavPath)
    
    # Process audio with the processor
    input_values = processor(audio, return_tensors="pt", sampling_rate=16000).input_values
    input_values = input_values.to(device)
    
    # Get embeddings
    with torch.no_grad():
        outputs = model(input_values)
        vec = outputs.last_hidden_state.squeeze().cpu().numpy()
    
    np.save(vecPath, vec, allow_pickle=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--wav", help="wav", dest="wav", required=True)
    parser.add_argument("-v", "--vec", help="vec", dest="vec", required=True)
    
    args = parser.parse_args()
    print(args.wav)
    print(args.vec)
    os.makedirs(args.vec, exist_ok=True)

    wavPath = args.wav
    vecPath = args.vec

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, processor = load_model("facebook/data2vec-audio-large-100h", device)

    for spks in os.listdir(wavPath):
        if os.path.isdir(f"./{wavPath}/{spks}"):
            os.makedirs(f"./{vecPath}/{spks}", exist_ok=True)

            files = [f for f in os.listdir(f"./{wavPath}/{spks}") if f.endswith(".wav")]
            for file in tqdm(files, desc=f'Processing vec {spks}'):
                file = file[:-4]
                pred_vec(model, processor, f"{wavPath}/{spks}/{file}.wav", f"{vecPath}/{spks}/{file}.vec", device)
