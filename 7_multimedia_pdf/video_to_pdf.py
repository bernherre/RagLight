import os
from pathlib import Path
from datetime import timedelta

from tqdm import tqdm
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib import utils

from faster_whisper import WhisperModel


def format_timestamp(seconds: float) -> str:
    td = timedelta(seconds=seconds)
    # hh:mm:ss.mmm
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    ms = int((td.total_seconds() - total_seconds) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{ms:03d}"


def transcribe(
    video_path: str,
    model_size: str = "medium",
    device: str = "auto",
    compute_type: str = "auto",
    language: str | None = None,
):
    """
    model_size: tiny | base | small | medium | large-v3
    device: "cpu" | "cuda" | "auto"
    compute_type (GPU): "float16" | "int8_float16" ; (CPU) "int8" | "int8_float32" | "auto"
    language: ISO 639-1 code (e.g., 'en', 'es', 'de'). If None, auto-detect.
    """
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    segments, info = model.transcribe(
        video_path,
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
        word_timestamps=False,
        language=language,  # 👈 added
    )
    return segments, info


def save_pdf(transcript_segments, info, pdf_path: str, title: str = None, include_timestamps: bool = True):
    doc = SimpleDocTemplate(pdf_path, pagesize=LETTER, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    story = []

    title = title or f"Transcript – {Path(pdf_path).stem}"
    story.append(Paragraph(title, styles["Title"]))
    meta = f"Language: {info.language} | Language prob: {info.language_probability:.2f}"
    story.append(Paragraph(meta, styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    # Armar el cuerpo
    for seg in transcript_segments:
        start = format_timestamp(seg.start)
        end = format_timestamp(seg.end)
        text = seg.text.strip()

        if include_timestamps:
            para = Paragraph(f"<b>[{start} → {end}]</b> {text}", styles["BodyText"])
        else:
            para = Paragraph(text, styles["BodyText"])

        story.append(para)
        story.append(Spacer(1, 0.15 * inch))

    doc.build(story)


def save_txt(transcript_segments, txt_path: str, include_timestamps: bool = True):
    with open(txt_path, "w", encoding="utf-8") as f:
        for seg in transcript_segments:
            if include_timestamps:
                f.write(f"[{format_timestamp(seg.start)} → {format_timestamp(seg.end)}] {seg.text.strip()}\n")
            else:
                f.write(seg.text.strip() + "\n")


def save_srt(transcript_segments, srt_path: str):
    def srt_timestamp(seconds: float) -> str:
        td = timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        ms = int((td.total_seconds() - total_seconds) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(transcript_segments, start=1):
            f.write(f"{i}\n")
            f.write(f"{srt_timestamp(seg.start)} --> {srt_timestamp(seg.end)}\n")
            f.write(seg.text.strip() + "\n\n")


def main(video_path: str, out_basename: str | None = None, model_size: str = "medium", timestamps=True):
    video_path = Path(video_path)
    assert video_path.exists(), f"Video not found: {video_path}"

    out_basename = out_basename or video_path.with_suffix("").name
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = out_dir / f"{out_basename}.pdf"
    txt_path = out_dir / f"{out_basename}.txt"
    srt_path = out_dir / f"{out_basename}.srt"

    print(f"[1/3] Transcribing: {video_path} (model={model_size}) …")
    segments_gen, info = transcribe(str(video_path), model_size=model_size, device="auto", compute_type="auto")

    # materializar generador en lista para reutilizar
    segments = []
    for seg in tqdm(segments_gen, desc="Segments"):
        segments.append(seg)

    print(f"[2/3] Writing PDF → {pdf_path}")
    save_pdf(segments, info, str(pdf_path), title=f"Transcript: {video_path.name}", include_timestamps=timestamps)

    print(f"[3/3] Writing TXT/SRT → {txt_path}, {srt_path}")
    save_txt(segments, str(txt_path), include_timestamps=timestamps)
    save_srt(segments, str(srt_path))

    print("✅ Done.")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Transcribe a video and export PDF/TXT/SRT.")
    ap.add_argument("video", help="Path to the video file (mp4, mkv, mov, etc.)")
    ap.add_argument("--name", help="Output base name (without extension)", default=None)
    ap.add_argument("--model", help="Whisper model size (tiny|base|small|medium|large-v3)", default="medium")
    ap.add_argument("--language", help="Force language code (e.g., en, es, de). Default: auto", default=None)
    ap.add_argument("--no-timestamps", action="store_true", help="Do not include timestamps in outputs")
    args = ap.parse_args()

    main(
        args.video,
        out_basename=args.name,
        model_size=args.model,
        timestamps=not args.no_timestamps,
    )
