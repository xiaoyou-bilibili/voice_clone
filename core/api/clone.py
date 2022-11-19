import yaml

import numpy as np
import torch
import torchaudio
import librosa
from scipy.io.wavfile import write
from utils.JDC.model import JDCNet
from parallel_wavegan.utils import load_model
import time
from core.star.interface import build_model

to_mel = torchaudio.transforms.MelSpectrogram(
    n_mels=80, n_fft=2048, win_length=1200, hop_length=300)
mean, std = -4, 4

# 加载模型
# 加载JDC模型
F0_model = JDCNet(num_class=1, seq_len=192)
params = torch.load("utils/JDC/bst.t7")['net']
F0_model.load_state_dict(params)
_ = F0_model.eval()
F0_model = F0_model.to('cuda')
# 加载vocoder模型
vocoder = load_model("model/vocoder/checkpoint-400000steps.pkl").to('cuda').eval()
vocoder.remove_weight_norm()
_ = vocoder.eval()
# 加载训练好的模型
model_path = 'model/weight/epoch_00250.pth'
with open('model/weight/config.yml') as f:
    starganv2_config = yaml.safe_load(f)
starganv2 = build_model(model_params=starganv2_config["model_params"])
params = torch.load(model_path, map_location='cpu')
params = params['model_ema']
_ = [starganv2[key].load_state_dict(params[key]) for key in starganv2]
_ = [starganv2[key].eval() for key in starganv2]
starganv2.style_encoder = starganv2.style_encoder.to('cuda')
starganv2.mapping_network = starganv2.mapping_network.to('cuda')
starganv2.generator = starganv2.generator.to('cuda')


# 数据预处理
def preprocess(wave):
    wave_tensor = torch.from_numpy(wave).float()
    mel_tensor = to_mel(wave_tensor)
    mel_tensor = (torch.log(1e-5 + mel_tensor.unsqueeze(0)) - mean) / std
    return mel_tensor


# 风格计算
def compute_style(speaker_dicts):
    reference_embeddings = {}
    for key, (path, speaker) in speaker_dicts.items():
        if path == "":
            label = torch.LongTensor([speaker]).to('cuda')
            latent_dim = starganv2.mapping_network.shared[0].in_features
            ref = starganv2.mapping_network(torch.randn(1, latent_dim).to('cuda'), label)
        else:
            wave, sr = librosa.load(path, sr=24000)
            audio, index = librosa.effects.trim(wave, top_db=30)
            if sr != 24000:
                wave = librosa.resample(wave, sr, 24000)
            mel_tensor = preprocess(wave).to('cuda')

            with torch.no_grad():
                label = torch.LongTensor([speaker])
                ref = starganv2.style_encoder(mel_tensor.unsqueeze(1), label)
        reference_embeddings[key] = (ref, label)

    return reference_embeddings


# print('Original (vocoder):')
# wave, sr = librosa.load(wav_path, sr=24000)
# mel = preprocess(wave)
# c = mel.transpose(-1, -2).squeeze().to('cuda')
# with torch.no_grad():
#     recon = vocoder.inference(c)
#     recon = recon.view(-1).cpu().numpy()
# display(ipd.Audio(recon, rate=24000))
# print('Original:')
# display(ipd.Audio(wav_path, rate=24000))

def clone_voice(wav_path, out_path, speaks, refer_audio = ""):
    res = []

    # 先加载音频
    audio, source_sr = librosa.load(wav_path, sr=24000)
    audio = audio / np.max(np.abs(audio))
    audio.dtype = np.float32
    speaker_dicts = {}
    for speak in speaks:
        speaker_dicts['p' + str(speak)] = ('', speak)
    if refer_audio != "":
        speaker_dicts['p0'] = (refer_audio, 0)
    # 计算风格
    reference_embeddings = compute_style(speaker_dicts)
    # conversion
    start = time.time()
    # 对音频进行预处理
    source = preprocess(audio).to('cuda:0')
    keys = []
    converted_samples = {}
    reconstructed_samples = {}
    converted_mels = {}
    # 遍历所有的说话人并进行计算
    for key, (ref, _) in reference_embeddings.items():
        with torch.no_grad():
            f0_feat = F0_model.get_feature_GAN(source.unsqueeze(1))
            out = starganv2.generator(source.unsqueeze(1), ref, F0=f0_feat)

            c = out.transpose(-1, -2).squeeze().to('cuda')
            y_out = vocoder.inference(c)
            y_out = y_out.view(-1).cpu()

            if key not in speaker_dicts or speaker_dicts[key][0] == "":
                recon = None
            else:
                wave, sr = librosa.load(speaker_dicts[key][0], sr=24000)
                mel = preprocess(wave)
                c = mel.transpose(-1, -2).squeeze().to('cuda')
                recon = vocoder.inference(c)
                recon = recon.view(-1).cpu().numpy()

        converted_samples[key] = y_out.numpy()
        reconstructed_samples[key] = recon

        converted_mels[key] = out

        keys.append(key)
    end = time.time()
    print('total processing time: %.3f sec' % (end - start))
    # 把所有转换好的音频保存好
    for key, wave in converted_samples.items():
        write("{}/output_{}.wav".format(out_path, key), 24000, wave)
        res.append("output_{}.wav".format(key))
        # if reconstructed_samples[key] is not None:
        #     print("")
        #     write("out/output_{}.wav".format(key), 24000, reconstructed_samples[key])
        #     display(ipd.Audio(reconstructed_samples[key], rate=24000))
    return res
