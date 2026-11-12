"""
Transcribe long audio files using speech recognition, with chunking for length limits,
then write the transcript and an offline extractive summary to a Word document.
Requires ffmpeg on PATH for pydub to decode many formats.
"""

import argparse
import io
import math
import os
import re
import sys
import time
from collections import Counter
from dataclasses import dataclass
from typing import Optional

import speech_recognition as sr
from docx import Document
from pydub import AudioSegment
from pydub.utils import make_chunks

CHUNK_LENGTH_MS = 45000
RECOGNITION_ATTEMPTS = 3
PASSAGE_MAX_WORDS = 25
PASSAGE_MIN_WORDS = 8
KEY_TERM_COUNT = 15

# Common Indonesian function words and spoken fillers, ignored when scoring the summary.
STOPWORDS = frozenset(
    """
    ada adalah agak agar aja akan aku amat anda anu apa apakah atau bagaimana bagi
    bahkan bahwa baik banyak bapak baru begini begitu begitulah belum benar berapa
    berarti beliau biasa biasanya bilang bisa boleh bukan cuma cuman dah dalam dan
    dari deh dengan dia dong dulu engga enggak gimana gini gitu hal hanya harus hmm
    ibu ingin ini itu itulah iya jadi jika juga kali kalau kalian kalo kami kamu kan
    karena kata kayak kayaknya kemarin kemudian kenapa ketika kita kok kurang lagi
    lah lain lalu lebih lho loh macam maka mana masih masing mau memang mengenai
    mereka meski misalnya mungkin nah namanya nanti nggak ngomong nih orang pada pak
    para pengen pernah pun punya saat saja sama sampai sana sangat satu saya sebagai
    sebelum sebenarnya sedang sehingga sekali sekarang semua sendiri seperti sering
    setelah setiap siapa sih sini situ sudah supaya tadi tahu tapi tentang tersebut
    terus tetapi tiap toh trus tuh udah untuk waktu walaupun yaitu yakni yang yah
    """.split()
)


@dataclass
class Segment:
    start_ms: int
    end_ms: int
    text: Optional[str]  # None when no speech could be recognized


def format_timestamp(ms: int) -> str:
    seconds = ms // 1000
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def recognize_segment(
    recognizer: sr.Recognizer, audio_data: sr.AudioData, language: str, label: str
) -> Optional[str]:
    """Recognize one segment, retrying transient service errors so no audio is silently lost."""
    for attempt in range(1, RECOGNITION_ATTEMPTS + 1):
        try:
            return recognizer.recognize_google(audio_data, language=language)
        except sr.UnknownValueError:
            print(f" -> {label}: No clear speech detected.")
            return None
        except sr.RequestError as e:
            if attempt == RECOGNITION_ATTEMPTS:
                print(f" -> {label}: Recognition service error ({e})")
                return None
            print(f" -> {label}: Recognition service error ({e}), retrying...")
            time.sleep(2 * attempt)
    return None


def transcribe_long_audio(path_audio: str, language: str = "id-ID") -> list[Segment]:
    """Split audio into chunks, transcribe each, return one Segment per chunk."""
    recognizer = sr.Recognizer()

    print(f"Loading file: {path_audio}")
    try:
        if path_audio.lower().endswith(".m4a"):
            audio = AudioSegment.from_file(path_audio, format="m4a")
        else:
            audio = AudioSegment.from_file(path_audio)

        audio = audio.set_channels(1).set_frame_rate(16000)

    except Exception as e:
        raise RuntimeError(f"Error loading or converting audio: {e}") from e

    chunks = make_chunks(audio, CHUNK_LENGTH_MS)

    print(f"Audio split into {len(chunks)} segments for processing.\n")

    segments: list[Segment] = []
    for i, chunk in enumerate(chunks):
        print(f"Processing segment {i + 1} of {len(chunks)}...")
        label = f"Segment {i + 1}"
        start_ms = i * CHUNK_LENGTH_MS
        text = None

        try:
            wav = io.BytesIO()
            chunk.export(wav, format="wav")
            wav.seek(0)
            with sr.AudioFile(wav) as source:
                audio_data = recognizer.record(source)
            text = recognize_segment(recognizer, audio_data, language, label)
        except Exception as e:
            print(f" -> {label}: Unexpected error ({e})")

        segments.append(Segment(start_ms, start_ms + len(chunk), text))

    return segments


def content_words(text: str) -> list[str]:
    return [
        w
        for w in re.findall(r"[^\W\d_]+", text.lower())
        if len(w) >= 3 and w not in STOPWORDS
    ]


def split_passages(text: str) -> list[str]:
    """Split on sentence punctuation; cut long runs (speech output is often unpunctuated)."""
    passages = []
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        words = sentence.split()
        for i in range(0, len(words), PASSAGE_MAX_WORDS):
            passages.append(" ".join(words[i : i + PASSAGE_MAX_WORDS]))
    return passages


def summarize(
    segments: list[Segment], points: int
) -> tuple[list[tuple[Segment, str]], list[tuple[str, int]]]:
    """
    Offline extractive summary.

    Words are weighted by how often they occur in the whole transcript (stopwords
    excluded); each passage scores the average weight of its words. The transcript
    is divided into `points` consecutive parts and the best passage of each part is
    kept, so the summary follows the conversation from start to end.
    Returns (passages in chronological order, most frequent key terms with counts).
    """
    freq = Counter(w for s in segments if s.text for w in content_words(s.text))
    if not freq:
        return [], []
    top_count = freq.most_common(1)[0][1]

    candidates: list[tuple[Segment, str, float]] = []
    for segment in segments:
        if not segment.text:
            continue
        for passage in split_passages(segment.text):
            words = content_words(passage)
            if len(passage.split()) < PASSAGE_MIN_WORDS or not words:
                continue
            score = sum(freq[w] for w in words) / (top_count * len(words))
            candidates.append((segment, passage, score))

    if not candidates:
        return [], freq.most_common(KEY_TERM_COUNT)

    part_size = math.ceil(len(candidates) / points)
    summary = []
    for i in range(0, len(candidates), part_size):
        segment, passage, _ = max(candidates[i : i + part_size], key=lambda c: c[2])
        summary.append((segment, passage))

    return summary, freq.most_common(KEY_TERM_COUNT)


def save_to_word(
    segments: list[Segment],
    summary: list[tuple[Segment, str]],
    key_terms: list[tuple[str, int]],
    source_name: str,
    path_out: str,
) -> None:
    doc = Document()
    doc.add_heading("Audio transcription", 0)

    recognized = sum(1 for s in segments if s.text)
    doc.add_paragraph(f"Source file: {source_name}")
    doc.add_paragraph(f"Duration: {format_timestamp(segments[-1].end_ms)}")
    doc.add_paragraph(f"Segments recognized: {recognized} of {len(segments)}")

    doc.add_heading("Summary", 1)
    note = doc.add_paragraph().add_run(
        "Automatic extractive summary: the most representative passages of each part "
        "of the recording, in chronological order. Timestamps point to the full transcript."
    )
    note.italic = True

    terms = doc.add_paragraph()
    terms.add_run("Key terms: ").bold = True
    terms.add_run(", ".join(f"{word} ({count})" for word, count in key_terms))

    for segment, passage in summary:
        item = doc.add_paragraph(style="List Bullet")
        item.add_run(f"[{format_timestamp(segment.start_ms)}] ").bold = True
        item.add_run(passage)

    doc.add_heading("Full transcript", 1)
    for segment in segments:
        para = doc.add_paragraph()
        para.add_run(
            f"[{format_timestamp(segment.start_ms)} - {format_timestamp(segment.end_ms)}] "
        ).bold = True
        if segment.text:
            para.add_run(segment.text)
        else:
            para.add_run("(no speech recognized)").italic = True

    doc.save(path_out)
    print(f"\nDone. Word file saved to: {path_out}")


def positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be 1 or greater")
    return number


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Transcribe a long audio file and save the transcript with a summary "
            "as a .docx file."
        )
    )
    parser.add_argument(
        "input_audio",
        help="Path to the input audio file (e.g. .m4a, .mp3, .wav)",
    )
    parser.add_argument(
        "output_docx",
        help="Path for the output Word document (.docx)",
    )
    parser.add_argument(
        "--language",
        default="id-ID",
        help="BCP-47 language tag for recognition (default: id-ID for Indonesian)",
    )
    parser.add_argument(
        "--summary-points",
        type=positive_int,
        default=10,
        help="Number of passages in the summary (default: 10)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not os.path.isfile(args.input_audio):
        print(f"Input file not found: {args.input_audio}", file=sys.stderr)
        return 1

    out_dir = os.path.dirname(os.path.abspath(args.output_docx))
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    print("=" * 50)
    print("Starting transcription...")
    try:
        segments = transcribe_long_audio(args.input_audio, language=args.language)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        return 1

    if not any(s.text for s in segments):
        print("\nStopped: no text could be extracted from the audio.")
        return 1

    print("\nSummarizing...")
    summary, key_terms = summarize(segments, args.summary_points)
    save_to_word(
        segments,
        summary,
        key_terms,
        os.path.basename(args.input_audio),
        args.output_docx,
    )

    print("=" * 50)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
