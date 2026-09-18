# whisper-fieldwork

Batch transcription of qualitative research audio (interviews, court hearings, informal conversations) with [OpenAI Whisper](https://github.com/openai/whisper).

I wrote this as an undergraduate research assistant, when the research groups I worked with at FGV Direito Rio needed interviews transcribed faster than we could do by hand, and later reused it for the interviews in my two undergraduate theses (Law and Social Sciences), both on the notions of justice held by people affected by state violence. Manual transcription was the bottleneck of every project; this script removed it. It runs on Google Colab (free GPU) or locally.

## What it does

- Transcribes every audio file in a folder and writes one transcript per recording.
- Skips files already transcribed, so a session can be resumed after Colab disconnects.
- Output formats chosen for research use:
  - `txt`: one segment per line, optionally with `[start-end]` seconds so passages can be cited precisely in a paper or thesis;
  - `csv`: `start,end,text`, ready for import into qualitative coding software (Atlas.ti, NVivo, Taguette);
  - `srt`: subtitles, useful when reviewing video recordings of hearings.
- Language can be forced (`--lang pt`) to avoid misdetection on short or noisy recordings.

## Usage

```bash
pip install -r requirements.txt

python transcribe.py --audio ./audio --out ./transcripts --lang pt
python transcribe.py --audio ./audio --out ./transcripts --lang pt --timestamps
python transcribe.py --audio ./audio --out ./transcripts --lang pt --format csv --model medium
```

On Google Colab, open `transcribe_colab.ipynb`, mount Drive and point `--audio` to the folder with the recordings. The `large` model needs a GPU runtime; `medium` is a good trade-off on the free tier.

## Ethics and data

Recordings and transcripts are never committed to this repository (see `.gitignore`). All interviews were conducted with informed consent under the research groups' protocols, and interlocutors are pseudonymised in the written work. Whisper runs entirely on the machine or Colab instance; no audio is sent to a third-party API.

## Requirements

Python 3.9+, `ffmpeg` on the system path, and a GPU for the `medium` and `large` models.
