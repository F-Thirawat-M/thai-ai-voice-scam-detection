# RawNet2 — ฝั่ง Nattadol

`model.py` is derived from the RawNet2 baseline
in [Nattadol/thai-audio-deepfake](https://github.com/Nattadol/thai-audio-deepfake)
at commit `a0772432245d30601ee9e171006016fbc575f2d1`. That repository credits
Hemlata Tak and carries the MIT license in this directory. The pretrained
checkpoint is downloaded from ASVspoof and is not committed to this repository.

`detector.py` connects this model to the shared CLI. Configuration, download
scripts and the original license live together in this folder.

Prepare the checkpoint from the project root:

```powershell
.\.venv\Scripts\python.exe -m thai_spoof.rawnet2.setup_checkpoint
```

Run inference:

```powershell
.\.venv\Scripts\python.exe -m thai_spoof.cli infer --model rawnet2 --audio data\sample\your_voice.wav
```
