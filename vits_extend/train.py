import os
import time
import logging
import math
import tqdm
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributed import init_process_group
from torch.nn.parallel import DistributedDataParallel
import re

from vits_extend.dataloader import create_dataloader_train
from vits_extend.dataloader import create_dataloader_eval
from vits_extend.writer import MyWriter
from vits_extend.stft import TacotronSTFT
from vits_extend.stft_loss import MultiResolutionSTFTLoss
from vits_extend.validation import validate
from vits_decoder.discriminator import Discriminator
from vits.models import SynthesizerTrn
from vits import commons
from vits.losses import kl_loss
from vits.commons import clip_grad_value_
from vits_extend.vggishdfl import VGGishDFL

def load_part(model, saved_state_dict):
    if hasattr(model, 'module'):
        state_dict = model.module.state_dict()
    else:
        state_dict = model.state_dict()
    new_state_dict = {}
    for k, v in state_dict.items():
        if k.startswith('TODO'):
            new_state_dict[k] = v
        else:
            new_state_dict[k] = saved_state_dict[k]
    if hasattr(model, 'module'):
        model.module.load_state_dict(new_state_dict)
    else:
        model.load_state_dict(new_state_dict)
    return model


def load_model(model, saved_state_dict):
    if hasattr(model, 'module'):
        state_dict = model.module.state_dict()
    else:
        state_dict = model.state_dict()
    new_state_dict = {}
    for k, v in state_dict.items():
        try:
            new_state_dict[k] = saved_state_dict[k]
        except:
            print("%s is not in the checkpoint" % k)
            new_state_dict[k] = v
    if hasattr(model, 'module'):
        model.module.load_state_dict(new_state_dict)
    else:
        model.load_state_dict(new_state_dict)
    return model


def train(rank, args, chkpt_path, hp, hp_str):

    if args.num_gpus > 1:
        init_process_group(backend=hp.dist_config.dist_backend, init_method=hp.dist_config.dist_url,
                           world_size=hp.dist_config.world_size * args.num_gpus, rank=rank)

    torch.cuda.manual_seed(hp.train.seed)
    device = torch.device('cuda:{:d}'.format(rank))

    model_g = SynthesizerTrn(
        hp.data.filter_length // 2 + 1,
        hp.data.segment_size // hp.data.hop_length,
        hp).to(device)
    model_d = Discriminator(hp).to(device)

    optim_g = torch.optim.AdamW(model_g.parameters(),
                                lr=hp.train.learning_rate, betas=hp.train.betas, eps=hp.train.eps)
    optim_d = torch.optim.AdamW(model_d.parameters(),
                                lr=(hp.train.learning_rate / hp.train.accum_step), betas=hp.train.betas, eps=hp.train.eps)

    init_epoch = 1
    step = 0
    best_loss = float('inf')
    best_interval_loss = float('inf')
    last_best_interval = 0

    stft = TacotronSTFT(filter_length=hp.data.filter_length,
                        hop_length=hp.data.hop_length,
                        win_length=hp.data.win_length,
                        n_mel_channels=hp.data.mel_channels,
                        sampling_rate=hp.data.sampling_rate,
                        mel_fmin=hp.data.mel_fmin,
                        mel_fmax=hp.data.mel_fmax,
                        center=False,
                        device=device)
    # define logger, writer, valloader, stft at rank_zero
    if rank == 0:
        pth_dir = os.path.join(hp.log.pth_dir, args.name)
        log_dir = os.path.join(hp.log.log_dir, args.name)
        os.makedirs(pth_dir, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, '%s-%d.log' % (args.name, time.time()))),
                logging.StreamHandler()
            ]
        )
        logger = logging.getLogger()
        writer = MyWriter(hp, log_dir)
        valloader = create_dataloader_eval(hp)

    if os.path.isfile(hp.train.pretrain):
        if rank == 0:
            logger.info("Start from 32k pretrain model: %s" % hp.train.pretrain)
        checkpoint = torch.load(hp.train.pretrain, map_location='cpu')
        load_model(model_g, checkpoint['model_g'])
        load_model(model_d, checkpoint['model_d'])

    if chkpt_path is not None:
        if rank == 0:
            logger.info("Resuming from checkpoint: %s" % chkpt_path)
        checkpoint = torch.load(chkpt_path, map_location='cpu')
        load_model(model_g, checkpoint['model_g'])
        load_model(model_d, checkpoint['model_d'])
        if hp.train.load_optim:
            logger.info("Load optim")
            optim_g.load_state_dict(checkpoint['optim_g'])
            optim_d.load_state_dict(checkpoint['optim_d'])
        else:
            logger.info("use config lr")
        init_epoch = checkpoint['epoch']
        step = checkpoint['step']
        if 'best_loss' in checkpoint:
            best_loss = checkpoint['best_loss']
            if rank == 0:
                logger.info(f"Loaded best loss: {best_loss}")

        if rank == 0:
            if hp_str != checkpoint['hp_str']:
                logger.warning("New hparams is different from checkpoint. Will use new.")
    else:
        if rank == 0:
            logger.info("Starting new training run.")

    if args.num_gpus > 1:
        model_g = DistributedDataParallel(model_g, device_ids=[rank])
        model_d = DistributedDataParallel(model_d, device_ids=[rank])

    # this accelerates training when the size of minibatch is always consistent.
    # if not consistent, it'll horribly slow down.
    torch.backends.cudnn.benchmark = True

    scheduler_g = torch.optim.lr_scheduler.ExponentialLR(optim_g, gamma=hp.train.lr_decay
                                                        #  , last_epoch=init_epoch-2
                                                         )
    scheduler_d = torch.optim.lr_scheduler.ExponentialLR(optim_d, gamma=hp.train.lr_decay
                                                        #  , last_epoch=init_epoch-2
                                                         )

    stft_criterion = MultiResolutionSTFTLoss(device, eval(hp.mrd.resolutions))
    spkc_criterion = nn.CosineEmbeddingLoss()

    trainloader = create_dataloader_train(hp, args.num_gpus, rank)
    vggish_criterion = VGGishDFL(pretrained=True).to(device,non_blocking=True)
    
    # Check if we should use best model saving
    use_best_model = getattr(hp.log, 'save_best', False)
    best_interval = getattr(hp.log, 'best_interval', 100)
    
    for epoch in range(init_epoch, hp.train.epochs):

        trainloader.batch_sampler.set_epoch(epoch)

        if rank == 0 and epoch % hp.log.eval_interval == 0:
            with torch.no_grad():
                validate(hp, args, model_g, model_d, valloader, stft, writer, step, device)

        if rank == 0:
            loader = tqdm.tqdm(trainloader, desc='Loading train data')
        else:
            loader = trainloader

        model_g.train()
        model_d.train()
        
        # Track average loss for this epoch
        epoch_g_loss_sum = 0.0
        epoch_g_loss_count = 0

        for ppg, ppg_l, vec, pit, spk, spec, spec_l, audio, audio_l in loader:

            ppg = ppg.to(device,non_blocking=True)
            vec = vec.to(device,non_blocking=True)
            pit = pit.to(device,non_blocking=True)
            spk = spk.to(device,non_blocking=True)
            spec = spec.to(device,non_blocking=True)
            audio = audio.to(device,non_blocking=True)
            ppg_l = ppg_l.to(device,non_blocking=True)
            spec_l = spec_l.to(device,non_blocking=True)
            audio_l = audio_l.to(device,non_blocking=True)

            # generator
            fake_audio, ids_slice, z_mask, \
                (z_f, z_r, z_p, m_p, logs_p, z_q, m_q, logs_q, logdet_f, logdet_r), spk_preds = model_g(
                    ppg, vec, pit, spec, spk, ppg_l, spec_l)

            audio = commons.slice_segments(
                audio, ids_slice * hp.data.hop_length, hp.data.segment_size)  # slice
            # VGGish Loss
            

            vggish_criterion.eval()
            vggish_loss = vggish_criterion(fake_audio.squeeze(1), audio.squeeze(1)) * hp.train.c_VGG
            # Spk Loss
            spk_loss = spkc_criterion(spk, spk_preds, torch.Tensor(spk_preds.size(0))
                                .to(device,non_blocking=True).fill_(1.0))
            # Mel Loss
            mel_fake = stft.mel_spectrogram(fake_audio.squeeze(1))
            mel_real = stft.mel_spectrogram(audio.squeeze(1))
            mel_loss = F.l1_loss(mel_fake, mel_real) * hp.train.c_mel

            # Mel Cepstrum Loss
            mel_cepstrum_fake = stft.mel_cepstrum(fake_audio.squeeze(1))
            mel_cepstrum_real = stft.mel_cepstrum(audio.squeeze(1))
            mel_cepstrum_loss = F.l1_loss(mel_cepstrum_fake, mel_cepstrum_real) * hp.train.c_mel_cepstrum

            # Multi-Resolution STFT Loss
            sc_loss, mag_loss = stft_criterion(fake_audio.squeeze(1), audio.squeeze(1))
            stft_loss = (sc_loss + mag_loss) * hp.train.c_stft

            # Phase Consistency Loss
            phase_fake = torch.angle(torch.stft(fake_audio.squeeze(1), n_fft=hp.data.filter_length, 
                                               hop_length=hp.data.hop_length, 
                                               win_length=hp.data.win_length, 
                                               return_complex=True))
            phase_real = torch.angle(torch.stft(audio.squeeze(1), n_fft=hp.data.filter_length, 
                                               hop_length=hp.data.hop_length, 
                                               win_length=hp.data.win_length, 
                                               return_complex=True))
            phase_loss = F.l1_loss(phase_fake, phase_real) * hp.train.c_pcl

            # High-Frequency Emphasis Loss
            # Extract high frequency components from mel spectrograms
            high_freq_mel_fake = mel_fake[:, hp.data.mel_channels//2:, :]
            high_freq_mel_real = mel_real[:, hp.data.mel_channels//2:, :]
            hf_loss = F.l1_loss(high_freq_mel_fake, high_freq_mel_real) * hp.train.c_hf

            # Generator Loss
            disc_fake = model_d(fake_audio)
            score_loss = 0.0
            for (_, score_fake) in disc_fake:
                score_loss += torch.mean(torch.pow(score_fake - 1.0, 2))
            score_loss = score_loss / len(disc_fake)

            # Feature Loss
            disc_real = model_d(audio)
            feat_loss = 0.0
            for (feat_fake, _), (feat_real, _) in zip(disc_fake, disc_real):
                for fake, real in zip(feat_fake, feat_real):
                    feat_loss += torch.mean(torch.abs(fake - real))
            feat_loss = feat_loss / len(disc_fake)
            feat_loss = feat_loss * 2

            # Kl Loss
            loss_kl_f = kl_loss(z_f, logs_q, m_p, logs_p, logdet_f, z_mask) * hp.train.c_kl
            loss_kl_r = kl_loss(z_r, logs_p, m_q, logs_q, logdet_r, z_mask) * hp.train.c_kl

            # Loss
            orig_loss_g = score_loss + feat_loss + mel_loss + stft_loss + loss_kl_f + loss_kl_r * 0.5 + spk_loss * 2
            loss_g = orig_loss_g + vggish_loss + phase_loss + hf_loss + mel_cepstrum_loss
            loss_g.backward()

            if ((step + 1) % hp.train.accum_step == 0) or (step + 1 == len(loader)):
                # accumulate gradients for accum steps
                for param in model_g.parameters():
                    param.grad /= hp.train.accum_step
                clip_grad_value_(model_g.parameters(),  None)
                # update model
                optim_g.step()
                optim_g.zero_grad()

            # discriminator
            optim_d.zero_grad()
            disc_fake = model_d(fake_audio.detach())
            disc_real = model_d(audio)

            loss_d = 0.0
            for (_, score_fake), (_, score_real) in zip(disc_fake, disc_real):
                loss_d += torch.mean(torch.pow(score_real - 1.0, 2))
                loss_d += torch.mean(torch.pow(score_fake, 2))
            loss_d = loss_d / len(disc_fake)

            loss_d.backward()
            clip_grad_value_(model_d.parameters(),  None)
            optim_d.step()

            step += 1
            # logging
            loss_g = loss_g.item()
            loss_d = loss_d.item()
            loss_s = stft_loss.item()
            loss_m = mel_loss.item()
            loss_k = loss_kl_f.item()
            loss_r = loss_kl_r.item()
            loss_i = spk_loss.item()
            loss_v = vggish_loss.item()
            loss_p = phase_loss.item()
            loss_h = hf_loss.item()
            loss_mc = mel_cepstrum_loss.item()
            o_loss_g = orig_loss_g.item()
            
            # Track average loss for best model saving
            epoch_g_loss_sum += o_loss_g
            epoch_g_loss_count += 1
            
            current_lr = scheduler_g.get_last_lr()[0]
            if rank == 0 and step % hp.log.info_interval == 0:
                writer.log_training(
                    o_loss_g, loss_d, loss_m, loss_s, loss_k, loss_r, score_loss.item(), loss_v, loss_p, loss_h, loss_mc, step, current_lr)
                logger.info("epoch %d | o_g %.04f g %.04f m %.04f s %.04f d %.04f k %.04f r %.04f i %.04f v %.04f p %.04f h %.04f mc %.04f | step %d" % (
                    epoch, o_loss_g, loss_g, loss_m, loss_s, loss_d, loss_k, loss_r, loss_i, loss_v, loss_p, loss_h, loss_mc, step))

        # Calculate average loss for this epoch
        if rank == 0 and epoch_g_loss_count > 0:
            avg_g_loss = epoch_g_loss_sum / epoch_g_loss_count
            logger.info(f"Epoch {epoch} average generator loss: {avg_g_loss:.4f}")
            
            # Save model based on strategy
            if use_best_model:
                current_interval = epoch // best_interval
                if current_interval > last_best_interval:
                    # Reset best loss for new interval
                    best_interval_loss = float('inf')
                    last_best_interval = current_interval
                
                # Save if this is the best model in current interval
                if avg_g_loss < best_interval_loss:
                    best_interval_loss = avg_g_loss
                    save_path = os.path.join(pth_dir, f'{args.name}_best_{current_interval * best_interval}-{(current_interval + 1) * best_interval}.pt')
                    torch.save({
                        'model_g': (model_g.module if args.num_gpus > 1 else model_g).state_dict(),
                        'model_d': (model_d.module if args.num_gpus > 1 else model_d).state_dict(),
                        'optim_g': optim_g.state_dict(),
                        'optim_d': optim_d.state_dict(),
                        'step': step,
                        'epoch': epoch,
                        'hp_str': hp_str,
                        'best_loss': best_interval_loss,
                    }, save_path)
                    logger.info(f"Saved best model for interval {current_interval * best_interval}-{(current_interval + 1) * best_interval} with loss {best_interval_loss:.4f} to: {save_path}")
                    
            elif epoch % hp.log.save_interval == 0:
                # Save based on interval if not using best model strategy
                save_path = os.path.join(pth_dir, f'{args.name}_{epoch:04d}.pt')
                torch.save({
                    'model_g': (model_g.module if args.num_gpus > 1 else model_g).state_dict(),
                    'model_d': (model_d.module if args.num_gpus > 1 else model_d).state_dict(),
                    'optim_g': optim_g.state_dict(),
                    'optim_d': optim_d.state_dict(),
                    'step': step,
                    'epoch': epoch,
                    'hp_str': hp_str,
                }, save_path)
                logger.info(f"Saved checkpoint to: {save_path}")

        if rank == 0:
            def clean_checkpoints(path_to_models=f'{pth_dir}', n_ckpts_to_keep=hp.log.keep_ckpts, sort_by_time=True):
                """Freeing up space by deleting saved ckpts
                Arguments:
                path_to_models    --  Path to the model directory
                n_ckpts_to_keep   --  Number of ckpts to keep per interval when using best model saving
                                      If n_ckpts_to_keep == 0, do not delete any ckpts
                sort_by_time      --  True -> chronologically delete ckpts
                                      False -> lexicographically delete ckpts
                """
                assert isinstance(n_ckpts_to_keep, int) and n_ckpts_to_keep >= 0
                ckpts_files = [f for f in os.listdir(path_to_models) if os.path.isfile(os.path.join(path_to_models, f))]
                
                if use_best_model:
                    # Group checkpoints by interval
                    interval_ckpts = {}
                    for f in ckpts_files:
                        if f.startswith(f'{args.name}_') and f.endswith('.pt'):
                            # Extract interval from filename
                            interval_match = re.search(r'best_(\d+)-\d+\.pt$', f)
                            if interval_match:
                                interval_start = int(interval_match.group(1))
                                if interval_start not in interval_ckpts:
                                    interval_ckpts[interval_start] = []
                                interval_ckpts[interval_start].append(f)
                    
                    # Keep only n_ckpts_to_keep files per interval
                    to_del = []
                    for interval, files in interval_ckpts.items():
                        if n_ckpts_to_keep > 0:
                            files.sort(key=lambda f: os.path.getmtime(os.path.join(path_to_models, f)) if sort_by_time else f)
                            to_del.extend([os.path.join(path_to_models, f) for f in files[:-n_ckpts_to_keep]])
                else:
                    # Original behavior for non-best-model saving
                    name_key = (lambda _f: int(re.compile(f'{args.name}_(\d+)\.pt').match(_f).group(1)))
                    time_key = (lambda _f: os.path.getmtime(os.path.join(path_to_models, _f)))
                    sort_key = time_key if sort_by_time else name_key
                    x_sorted = lambda _x: sorted([f for f in ckpts_files if f.startswith(_x) and not f.endswith('sovits5.0_0.pth')], key=sort_key)
                    if n_ckpts_to_keep == 0:
                        to_del = []
                    else:
                        to_del = [os.path.join(path_to_models, fn) for fn in x_sorted(f'{args.name}')[:-n_ckpts_to_keep]]
                
                del_info = lambda fn: logger.info(f"Free up space by deleting ckpt {fn}")
                del_routine = lambda x: [os.remove(x), del_info(x)]
                rs = [del_routine(fn) for fn in to_del]

            clean_checkpoints()

            os.makedirs(f'{pth_dir}', exist_ok=True)
            keep_ckpts = getattr(hp.log, 'keep_ckpts', 0)
            if keep_ckpts > 0:
                clean_checkpoints(path_to_models=f'{pth_dir}', n_ckpts_to_keep=hp.log.keep_ckpts, sort_by_time=True)

        scheduler_g.step()
        scheduler_d.step()
