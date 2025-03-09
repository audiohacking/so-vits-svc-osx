import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import argparse
import torch

from whisper.model import Whisper, ModelDimensions
from whisper.audio import load_audio, pad_or_trim, log_mel_spectrogram


def load_model(path, device) -> Whisper:
    checkpoint = torch.load(path, map_location="cpu")
    dims = ModelDimensions(**checkpoint["dims"])
    # print(dims)
    model = Whisper(dims)
    del model.decoder
    cut = len(model.encoder.blocks) // 4
    cut = -1 * cut
    del model.encoder.blocks[cut:]
    model.load_state_dict(checkpoint["model_state_dict"], strict=False)
    model.eval()
    model.to(device)
    return model


def pred_ppg(whisper_v2: Whisper, whisper_v3: Whisper, wavPath, ppgPath, device):
    audio = load_audio(wavPath)
    audln = audio.shape[0]
    ppg_a = []
    idx_s = 0
    while (idx_s + 15 * 16000 < audln):
        short = audio[idx_s:idx_s + 15 * 16000]
        idx_s = idx_s + 15 * 16000
        ppgln = 15 * 16000 // 320
        short = pad_or_trim(short)
        mel_v2 = log_mel_spectrogram(short, n_mels=80).to(device)
        mel_v3 = log_mel_spectrogram(short, n_mels=128).to(device)
        with torch.no_grad():
            # Add noise for augmentation
            mel_v2 = mel_v2 + torch.randn_like(mel_v2) * 0.01
            mel_v3 = mel_v3 + torch.randn_like(mel_v3) * 0.01
            
            # Process with whisper v2
            ppg_v2 = whisper_v2.encoder(mel_v2.unsqueeze(0)).squeeze().data.cpu().float().numpy()
            ppg_v2 = ppg_v2[:ppgln,]  # [length, dim=1280]
            
            # Process with whisper v3
            ppg_v3 = whisper_v3.encoder(mel_v3.unsqueeze(0)).squeeze().data.cpu().float().numpy()
            ppg_v3 = ppg_v3[:ppgln,]  # [length, dim=1280]
            
            # Average features from both models
            ppg = ppg_v2*0.4 + ppg_v3*0.6  # [length, dim=1280]
            ppg_a.extend(ppg)
    
    if (idx_s < audln):
        short = audio[idx_s:audln]
        ppgln = (audln - idx_s) // 320
        short = pad_or_trim(short)
        mel_v2 = log_mel_spectrogram(short, n_mels=80).to(device)
        mel_v3 = log_mel_spectrogram(short, n_mels=128).to(device)
        with torch.no_grad():
            # Add noise for augmentation
            mel_v2 = mel_v2 + torch.randn_like(mel_v2) * 0.01
            mel_v3 = mel_v3 + torch.randn_like(mel_v3) * 0.01
            
            # Process with whisper v2
            ppg_v2 = whisper_v2.encoder(mel_v2.unsqueeze(0)).squeeze().data.cpu().float().numpy()
            ppg_v2 = ppg_v2[:ppgln,]  # [length, dim=1280]
            
            # Process with whisper v3
            ppg_v3 = whisper_v3.encoder(mel_v3.unsqueeze(0)).squeeze().data.cpu().float().numpy()
            ppg_v3 = ppg_v3[:ppgln,]  # [length, dim=1280]
            
            # Average features from both models
            ppg = ppg_v2*0.4 + ppg_v3*0.6  # [length, dim=1280]
            ppg_a.extend(ppg)
    
    np.save(ppgPath, ppg_a, allow_pickle=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--wav", help="wav", dest="wav", required=True)
    parser.add_argument("-p", "--ppg", help="ppg", dest="ppg", required=True)
    args = parser.parse_args()
    print(args.wav)
    print(args.ppg)

    wavPath = args.wav
    ppgPath = args.ppg

    device = "cuda" if torch.cuda.is_available() else "cpu"
    whisper_v2 = load_model(os.path.join("whisper_pretrain", "large-v2.pt"), device)
    whisper_v3 = load_model(os.path.join("whisper_pretrain", "large-v3.pt"), device)
    pred_ppg(whisper_v2, whisper_v3, wavPath, ppgPath, device)
