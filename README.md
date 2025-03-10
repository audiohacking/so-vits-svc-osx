<div align="center">
<h1> Variational Inference with adversarial learning for end-to-end Singing Voice Conversion based on VITS </h1>
    
[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/maxmax20160403/sovits5.0)
<img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/PlayVoice/so-vits-svc-5.0">
<img alt="GitHub forks" src="https://img.shields.io/github/forks/PlayVoice/so-vits-svc-5.0">
<img alt="GitHub issues" src="https://img.shields.io/github/issues/PlayVoice/so-vits-svc-5.0">
<img alt="GitHub" src="https://img.shields.io/github/license/PlayVoice/so-vits-svc-5.0">

<div>
<div align="left">

## 5.2 Update by HorikitaSaku

- Whisper now uses a fusion of v2 and v3 models for better content encoding
- Replaced CREPE with RMVPE (Robust Model for Pitch Extraction) for more accurate pitch detection
- Referenced implementation techniques from:
  - [whisper-vits-svc (bigvgan-mix-v2 branch)](https://github.com/PlayVoice/whisper-vits-svc/tree/bigvgan-mix-v2)
  - [Retrieval-based-Voice-Conversion-WebUI](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/tree/main)
- Adding ContentVec/data2vec
- Adding phase loss/high frequency mel loss/vggish loss

## Setup Environment

1. Install [PyTorch](https://pytorch.org/get-started/locally/).

2. Install project dependencies
    ```shell
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
    ```
    **Note: whisper is already built-in, do not install it again otherwise it will cuase conflict and error**
3. Download the Timbre Encoder: [Speaker-Encoder by @mueller91](https://drive.google.com/drive/folders/15oeBYf6Qn1edONkVLXe82MzdIi3O_9m3), put `best_model.pth.tar`  into `speaker_pretrain/`.

4. Download whisper model [whisper-large-v2](https://openaipublic.azureedge.net/main/whisper/models/81f7c96c852ee8fc832187b0132e569d6c3065a3252ed18e56effd0b6a73e524/large-v2.pt) or [whisper-large-v3](https://openaipublic.azureedge.net/main/whisper/models/e5b1a55b89c1367dacf97e3e19bfd829a01529dbfdeefa8caeb59b3f1b81dadb/large-v3.pt). Make sure to download the model file and put it into `whisper_pretrain/`.

5. Download [hubert_soft model](https://github.com/bshall/hubert/releases/tag/v0.1)，put `hubert-soft-0d54a1f4.pt` into `hubert_pretrain/`.

6. Download RMVPE model and put `rmvpe.pt` into `rmvpe_pretrain/`.

7. Download pretrain model [sovits5.0.pretrain.pth](https://github.com/PlayVoice/so-vits-svc-5.0/releases/tag/5.0/), and put it into `vits_pretrain/`.
    ```shell
    python svc_inference.py --config configs/base.yaml --model ./vits_pretrain/sovits5.0.pretrain.pth --spk ./configs/singers/singer0001.npy --wave test.wav
    ```

## Dataset preparation

Necessary pre-processing:
1. Separate voice and accompaniment with [UVR](https://github.com/Anjok07/ultimatevocalremovergui) (skip if no accompaniment)
2. Cut audio input to shorter length with [slicer](https://github.com/flutydeer/audio-slicer), whisper takes input less than 30 seconds.
3. Manually check generated audio input, remove inputs shorter than 2 seconds or with obivous noise.
4. Adjust loudness if necessary, recommend Adobe Audiiton.
5. Put the dataset into the `dataset_raw` directory following the structure below.
<div>
