import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import argparse
import torch
import librosa

from tqdm import tqdm
from contentvec.get_hubert import get_hubert_model
from utils.device import get_device, get_device_name


def load_audio(file: str, sr: int = 16000):
    x, sr = librosa.load(file, sr=sr)
    return x


def load_model(path, device):
    model = get_hubert_model(path, device)
    model.eval()
    return model


def pred_vec(model, wavPath, vecPath, device):
    audio = load_audio(wavPath)
    audln = audio.shape[0]
    vec_a = []
    idx_s = 0
    

    feats = audio[idx_s:audln]
    feats = torch.from_numpy(feats).to(device)
    feats = feats.unsqueeze(0)
    with torch.no_grad():
        vec = model.infer(source=feats, padding_mask=None, output_layer=torch.tensor(9)).squeeze().data.cpu().float().numpy()
        vec_a.extend(vec)

    np.save(vecPath, vec_a, allow_pickle=False)


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

    device = get_device()
    print(f"Using device: {get_device_name(device)}")
    hubert = load_model(os.path.join("contentvec_pretrain", "checkpoint_best_legacy_500.pt"), device)

    for spks in os.listdir(wavPath):
        if os.path.isdir(f"./{wavPath}/{spks}"):
            os.makedirs(f"./{vecPath}/{spks}", exist_ok=True)

            files = [f for f in os.listdir(f"./{wavPath}/{spks}") if f.endswith(".wav")]
            for file in tqdm(files, desc=f'Processing vec {spks}'):
                file = file[:-4]
                pred_vec(hubert, f"{wavPath}/{spks}/{file}.wav", f"{vecPath}/{spks}/{file}.vec", device)
