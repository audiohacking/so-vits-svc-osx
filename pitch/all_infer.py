import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import torch
import librosa
import argparse
import numpy as np
import crepe
from rmvpe.RMVPE import RMVPE
from utils.device import get_device, get_device_name


def move_average(a, n, mode="same"):
    return (np.convolve(a, np.ones((n,))/n, mode=mode))


def compute_f0_mouth(path, device):
    # pip install praat-parselmouth
    import parselmouth

    x, sr = librosa.load(path, sr=16000)
    assert sr == 16000
    lpad = 1024 // 160
    rpad = lpad
    f0 = parselmouth.Sound(x, sr).to_pitch_ac(
        time_step=160 / sr,
        voicing_threshold=0.5,
        pitch_floor=30,
        pitch_ceiling=1000).selected_array['frequency']
    f0 = np.pad(f0, [[lpad, rpad]], mode='constant')
    return f0


def compute_f0_salience(filename, device):
    from pitch.core.salience import salience
    audio, sr = librosa.load(filename, sr=16000)
    assert sr == 16000
    f0, t, s = salience(
        audio,
        Fs=sr,
        H=320,
        N=2048,
        F_min=45.0,
        F_max=1760.0)
    f0 = np.repeat(f0, 2, -1)  # 320 -> 160 * 2
    f0 = move_average(f0, 3)
    return f0


def compute_f0_voice(filename, device, model_path):
    audio, sr = librosa.load(filename, sr=16000)
    assert sr == 16000
    audio = torch.tensor(np.copy(audio))
    audio = audio + torch.randn_like(audio) * 0.001
    
    # Initialize RMVPE model
    rmvpe = RMVPE(model_path, is_half=False, device=device)
    
    # Use RMVPE to infer pitch
    f0 = rmvpe.infer_from_audio(audio, thred=0.03)
    
    return f0


def compute_f0_sing(filename, device, model_path, crepe_weight=0.85, rmvpe_weight=0.15):
    # Load audio
    audio, sr = librosa.load(filename, sr=16000)
    assert sr == 16000
    
    # Get CREPE prediction
    audio_crepe = torch.tensor(np.copy(audio))[None]
    audio_crepe = audio_crepe + torch.randn_like(audio_crepe) * 0.001
    hop_length = 320
    fmin = 50
    fmax = 1000
    model = "full"
    batch_size = 512
    pitch_crepe = crepe.predict(
        audio_crepe,
        sr,
        hop_length,
        fmin,
        fmax,
        model,
        batch_size=batch_size,
        device=device,
        return_periodicity=False,
    )
    pitch_crepe = np.repeat(pitch_crepe, 2, -1)  # 320 -> 160 * 2
    pitch_crepe = crepe.filter.mean(pitch_crepe, 5)
    pitch_crepe = pitch_crepe.squeeze(0)
    
    # Get RMVPE prediction
    audio_rmvpe = torch.tensor(np.copy(audio))
    audio_rmvpe = audio_rmvpe + torch.randn_like(audio_rmvpe) * 0.001
    rmvpe = RMVPE(model_path, is_half=False, device=device)
    pitch_rmvpe = rmvpe.infer_from_audio(audio_rmvpe, thred=0.05)
    pitch_rmvpe = move_average(pitch_rmvpe, 5)
    
    # Combine predictions with weights
    f0 = pitch_crepe * crepe_weight + pitch_rmvpe * rmvpe_weight
    
    return f0


def save_csv_pitch(pitch, path):
    with open(path, "w", encoding='utf-8') as pitch_file:
        for i in range(len(pitch)):
            t = i * 10
            minute = t // 60000
            seconds = (t - minute * 60000) // 1000
            millisecond = t % 1000
            print(
                f"{minute}m {seconds}s {millisecond:3d},{int(pitch[i])}", file=pitch_file)


def load_csv_pitch(path):
    pitch = []
    with open(path, "r", encoding='utf-8') as pitch_file:
        for line in pitch_file.readlines():
            pit = line.strip().split(",")[-1]
            pitch.append(int(pit))
    return pitch


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--wav", help="wav", dest="wav", required=True)
    parser.add_argument("-p", "--pit", help="pit", dest="pit", required=True)  # csv for excel
    parser.add_argument("-m", "--model", help="Path to the RMVPE model", dest="model", default="rmvpe_pretrain/rmvpe.pt")
    parser.add_argument("--crepe-weight", type=float, default=0.8, help="Weight for CREPE prediction")
    parser.add_argument("--rmvpe-weight", type=float, default=0.2, help="Weight for RMVPE prediction")
    
    args = parser.parse_args()
    print(args.wav)
    print(args.pit)

    device = get_device()
    print(f"Using device: {get_device_name(device)}")
    pitch = compute_f0_sing(args.wav, device, args.model, args.crepe_weight, args.rmvpe_weight)
    save_csv_pitch(pitch, args.pit)
    # tmp = load_csv_pitch(args.pit)
    # save_csv_pitch(tmp, "tmp.csv")
