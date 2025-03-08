<div align="center">
<h1> Variational Inference with adversarial learning for end-to-end Singing Voice Conversion based on VITS </h1>
    
[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/maxmax20160403/sovits5.0)
<img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/PlayVoice/so-vits-svc-5.0">
<img alt="GitHub forks" src="https://img.shields.io/github/forks/PlayVoice/so-vits-svc-5.0">
<img alt="GitHub issues" src="https://img.shields.io/github/issues/PlayVoice/so-vits-svc-5.0">
<img alt="GitHub" src="https://img.shields.io/github/license/PlayVoice/so-vits-svc-5.0">

[中文文档](./README_ZH.md)

The tree [bigvgan-mix-v2](https://github.com/PlayVoice/whisper-vits-svc/tree/bigvgan-mix-v2) has good audio quality

The tree [RoFormer-HiFTNet](https://github.com/PlayVoice/whisper-vits-svc/tree/RoFormer-HiFTNet) has fast infer speed

No More Upgrade

</div>
- This project targets deep learning beginners, basic knowledge of Python and PyTorch are the prerequisites for this project;
- This project aims to help deep learning beginners get rid of boring pure theoretical learning, and master the basic knowledge of deep learning by combining it with practices;
- This project does not support real-time voice converting; (need to replace whisper if real-time voice converting is what you are looking for)
- This project will not develop one-click packages for other purposes;

![vits-5.0-frame](https://github.com/PlayVoice/so-vits-svc-5.0/assets/16432329/3854b281-8f97-4016-875b-6eb663c92466)

- A minimum VRAM requirement of 6GB for training

- Support for multiple speakers

- Create unique speakers through speaker mixing

- It can even convert voices with light accompaniment

- You can edit F0 using Excel

https://github.com/PlayVoice/so-vits-svc-5.0/assets/16432329/6a09805e-ab93-47fe-9a14-9cbc1e0e7c3a

Powered by [@ShadowVap](https://space.bilibili.com/491283091)

## Update
- Now supports both Whisper V2 and V3
- Replaced Crepe with RMVPE for pitch extraction

## Model properties

| Feature | From | Status | Function |
| :--- | :--- | :--- | :--- |
| whisper | OpenAI | ✅ | strong noise immunity |
| bigvgan  | NVIDA | ✅ | alias and snake | The formant is clearer and the sound quality is obviously improved |
| natural speech | Microsoft | ✅ | reduce mispronunciation |
| neural source-filter | Xin Wang | ✅ | solve the problem of audio F0 discontinuity |
| pitch quantization | Xin Wang | ✅ | quantize the F0 for embedding |
| speaker encoder | Google | ✅ | Timbre Encoding and Clustering |
| GRL for speaker | Ubisoft |✅ | Preventing Encoder Leakage Timbre |
| SNAC |  Samsung | ✅ | One Shot Clone of VITS |
| SCLN |  Microsoft | ✅ | Improve Clone |
| Diffusion |  HuaWei | ✅ | Improve sound quality |
| PPG perturbation | this project | ✅ | Improved noise immunity and de-timbre |
| HuBERT perturbation | this project | ✅ | Improved noise immunity and de-timbre |
| VAE perturbation | this project | ✅ | Improve sound quality |
| MIX encoder | this project | ✅ | Improve conversion stability |
| USP infer | this project | ✅ | Improve conversion stability |
| HiFTNet | Columbia University | ✅ | NSF-iSTFTNet for speed up |
| RoFormer | Zhuiyi Technology | ✅ | Rotary Positional Embeddings |

due to the use of data perturbation, it takes longer to train than other projects.

**USP : Unvoice and Silence with Pitch when infer**
![vits_svc_usp](https://github.com/PlayVoice/so-vits-svc-5.0/assets/16432329/ba733b48-8a89-4612-83e0-a0745587d150)

## Why mix

![mix_frame](https://github.com/PlayVoice/whisper-vits-svc/assets/16432329/3ffa1be0-1a21-4752-96b5-6220f98f2313)

## Plug-In-Diffusion

![plug-in-diffusion](https://github.com/PlayVoice/so-vits-svc-5.0/assets/16432329/54a61c90-a97b-404d-9cc9-a2151b2db28f)

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
