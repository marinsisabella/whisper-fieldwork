"""
Batch transcription of fieldwork audio (interviews, hearings, informal
conversations) with OpenAI Whisper.

Reads every audio file in a folder, transcribes it and writes one text file
per recording. Designed for qualitative research: the output can be plain
prose, timestamped segments (for citing passages in a paper or thesis), or a CSV
ready to be imported into a coding tool.

Usage:
    python transcribe.py --audio ./audio --out ./transcripts
    python transcribe.py --audio ./audio --out ./transcripts --model medium --lang pt --timestamps
    python transcribe.py --audio ./audio --out ./transcripts --format csv
"""

import argparse
import csv
import sys
from pathlib import Path

import whisper

AUDIO_EXTENSIONS = {".mp3", ".m4a", ".wav", ".ogg", ".flac", ".aac", ".mp4", ".webm"}


def parse_args():
    parser = argparse.ArgumentParser(description="Batch-transcribe audio files with Whisper.")
    parser.add_argument("--audio", required=True, type=Path, help="Folder containing the recordings.")
    parser.add_argument("--out", required=True, type=Path, help="Folder where transcripts are written.")
    parser.add_argument("--model", default="large", help="Whisper model size (tiny, base, small, medium, large).")
    parser.add_argument("--lang", default=None, help="Language code, e.g. pt. Omit for auto-detection.")
    parser.add_argument("--timestamps", action="store_true", help="Prefix each segment with start and end seconds.")
    parser.add_argument(
        "--format",
        choices=["txt", "csv", "srt"],
        default="txt",
        help="txt: one segment per line; csv: start,end,text for qualitative coding tools; srt: subtitles.",
    )
    parser.add_argument("--overwrite", action="store_true", help="Re-transcribe files that already have a transcript.")
    return parser.parse_args()


def fmt_srt_time(seconds: float) -> str:
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def write_txt(segments, path: Path, timestamps: bool):
    with path.open("w", encoding="utf-8") as f:
        for seg in segments:
            text = seg["text"].strip()
            if timestamps:
                f.write(f"[{int(seg['start'])}-{int(seg['end'])}] ")
            f.write(text + "\n")


def write_csv(segments, path: Path):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["start", "end", "text"])
        for seg in segments:
            writer.writerow([round(seg["start"], 2), round(seg["end"], 2), seg["text"].strip()])


def write_srt(segments, path: Path):
    with path.open("w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            f.write(f"{i}\n{fmt_srt_time(seg['start'])} --> {fmt_srt_time(seg['end'])}\n{seg['text'].strip()}\n\n")


def main():
    args = parse_args()

    if not args.audio.is_dir():
        sys.exit(f"Audio folder not found: {args.audio}")
    args.out.mkdir(parents=True, exist_ok=True)

    audios = sorted(p for p in args.audio.iterdir() if p.suffix.lower() in AUDIO_EXTENSIONS)
    if not audios:
        sys.exit("No audio files found.")
    print(f"{len(audios)} file(s) found. Loading Whisper '{args.model}'...")

    model = whisper.load_model(args.model)

    for audio in audios:
        target = args.out / f"{audio.stem}.{args.format}"
        if target.exists() and not args.overwrite:
            print(f"Skipping {audio.name} (transcript exists)")
            continue

        print(f"Transcribing {audio.name}")
        result = model.transcribe(str(audio), language=args.lang, verbose=False)
        segments = result["segments"]

        if args.format == "txt":
            write_txt(segments, target, args.timestamps)
        elif args.format == "csv":
            write_csv(segments, target)
        else:
            write_srt(segments, target)

        print(f"  -> {target}")

    print("Done.")


if __name__ == "__main__":
    main()
