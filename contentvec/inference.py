import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import argparse
import torch
import librosa

from contentvec.get_hubert import get_hubert_model


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
    
    # Process audio in chunks if needed
    while (idx_s + 20 * 16000 < audln):
        feats = audio[idx_s:idx_s + 20 * 16000]
        feats = torch.from_numpy(feats).to(device)
        feats = feats.unsqueeze(0)
        with torch.no_grad():
            vec = model.infer(source=feats, padding_mask=None, output_layer=torch.tensor(9)).squeeze().data.cpu().float().numpy()
            vec_a.extend(vec)
        idx_s = idx_s + 20 * 16000
    
    if (idx_s < audln):
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

    wavPath = args.wav
    vecPath = args.vec

    device = "cuda" if torch.cuda.is_available() else "cpu"
    hubert = load_model(os.path.join(
        "contentvec_pretrain", "checkpoint_best_legacy_500.pt"), device)
    pred_vec(hubert, wavPath, vecPath, device)
