import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import argparse
import torch
import random
from tqdm import tqdm
from whisper.model import Whisper, ModelDimensions
from whisper.audio import load_audio, pad_or_trim, log_mel_spectrogram


def load_model(path) -> Whisper:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    checkpoint = torch.load(path, map_location="cpu")
    dims = ModelDimensions(**checkpoint["dims"])
    print(dims)
    model = Whisper(dims)
    del model.decoder
    cut = len(model.encoder.blocks) // 4
    cut = -1 * cut
    del model.encoder.blocks[cut:]
    model.load_state_dict(checkpoint["model_state_dict"], strict=False)
    model.eval()
    model.to(device)
    return model


def pred_ppg(whisper_v2: Whisper, whisper_v3: Whisper, wavPath, ppgPath):
    audio = load_audio(wavPath)
    audln = audio.shape[0]
    ppgln = audln // 320
    audio = pad_or_trim(audio)
    mel_v2 = log_mel_spectrogram(audio, n_mels=80).float()
    mel_v3 = log_mel_spectrogram(audio, n_mels=128).float()
    with torch.no_grad():
        # Process with whisper v2
        mel_v2 = mel_v2.to(whisper_v2.device)
        ppg_v2 = whisper_v2.encoder(mel_v2.unsqueeze(0)).squeeze().data.cpu().float().numpy()
        ppg_v2 = ppg_v2[:ppgln,]  # [length, dim=1280]
        
        # Process with whisper v3
        mel_v3 = mel_v3.to(whisper_v3.device)
        ppg_v3 = whisper_v3.encoder(mel_v3.unsqueeze(0)).squeeze().data.cpu().float().numpy()
        ppg_v3 = ppg_v3[:ppgln,]  # [length, dim=1280]
        
        # Concatenate features from both models
        ppg = np.concatenate([ppg_v2, ppg_v3], axis=1)  # [length, dim=2560]
        
        print(ppg.shape)
        np.save(ppgPath, ppg, allow_pickle=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--wav", help="wav", dest="wav", required=True)
    parser.add_argument("-p", "--ppg", help="ppg", dest="ppg", required=True)
    args = parser.parse_args()
    print(args.wav)
    print(args.ppg)

    os.makedirs(args.ppg, exist_ok=True)
    wavPath = args.wav
    ppgPath = args.ppg

    whisper_v2 = load_model(os.path.join("whisper_pretrain", "large-v2.pt"))
    whisper_v3 = load_model(os.path.join("whisper_pretrain", "large-v3.pt"))
    spkPaths = os.listdir(wavPath)
    random.shuffle(spkPaths)

    for spks in spkPaths:
        if os.path.isdir(f"./{wavPath}/{spks}"):
            os.makedirs(f"./{ppgPath}/{spks}", exist_ok=True)

            files = [f for f in os.listdir(f"./{wavPath}/{spks}") if f.endswith(".wav")]
            for file in tqdm(files, desc=f'Processing ppg {spks}'):
                if file.endswith(".wav"):
                    # print(file)
                    file = file[:-4]
                    path_wav = f"{wavPath}/{spks}/{file}.wav"
                    path_ppg = f"{ppgPath}/{spks}/{file}.ppg"
                    if os.path.isfile(f"{path_ppg}.npy"):
                        continue
                    pred_ppg(whisper_v2, whisper_v3, path_wav, path_ppg)
