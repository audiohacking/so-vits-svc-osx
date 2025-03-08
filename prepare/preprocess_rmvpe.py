import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import librosa
import torch
import argparse
from tqdm import tqdm

# Import the RMVPE class from your RMVPE module
from rmvpe.RMVPE import RMVPE

def compute_f0(filename, save, rmvpe):
    # Load audio at 16 kHz
    audio, sr = librosa.load(filename, sr=16000)
    assert sr == 16000
    # Add random Gaussian noise to the audio (amplitude 0.01)
    noise = np.random.normal(0, 0.01, len(audio))
    audio = audio + noise
    # Convert audio to tensor
    audio_tensor = torch.tensor(audio)
    # Use RMVPE to infer pitch (f0) with a chosen threshold (0.03 here)
    f0 = rmvpe.infer_from_audio(audio_tensor, thred=0.03)
    # Save the resulting pitch contour as a .pit file
    np.save(save, f0, allow_pickle=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--wav", help="Directory containing wav files", dest="wav", required=True)
    parser.add_argument("-p", "--pit", help="Directory to save pitch files", dest="pit", required=True)
    parser.add_argument("-m", "--model", help="Path to the RMVPE model (.pt file)", dest="model", required=True)

    args = parser.parse_args()
    print("Wav directory:", args.wav)
    print("Pitch save directory:", args.pit)
    print("RMVPE model path:", args.model)

    os.makedirs(args.pit, exist_ok=True)
    wavPath = args.wav
    pitPath = args.pit

    # Choose the computation device
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Initialize RMVPE (here we use full precision; set is_half=True if desired)
    rmvpe = RMVPE(args.model, is_half=False, device=device)

    # Process each speaker directory
    for spks in os.listdir(wavPath):
        spk_dir = os.path.join(wavPath, spks)
        if os.path.isdir(spk_dir):
            os.makedirs(os.path.join(pitPath, spks), exist_ok=True)
            # Get list of .wav files in this speaker folder
            files = [f for f in os.listdir(spk_dir) if f.endswith(".wav")]
            for file in tqdm(files, desc=f'Processing RMVPE for {spks}'):
                basename = os.path.splitext(file)[0]
                wav_file = os.path.join(wavPath, spks, file)
                pit_file = os.path.join(pitPath, spks, f"{basename}.pit")
                compute_f0(wav_file, pit_file, rmvpe)
