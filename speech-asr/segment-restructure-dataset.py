from pydub import AudioSegment
import os
import shutil

# File paths
spkinfo_path = "D:/Buat-kuliah/Semester 7/deep-learning/speech-asr/Dataset-20241216T015426Z-001/Dataset/Indonesian_Conversational_Speech_Corpus/SPKINFO.txt"
audioinfo_path = "D:/Buat-kuliah/Semester 7/deep-learning/speech-asr/Dataset-20241216T015426Z-001/Dataset/Indonesian_Conversational_Speech_Corpus/AUDIOINFO.txt"
txt_dir = "D:/Buat-kuliah/Semester 7/deep-learning/speech-asr/Dataset-20241216T015426Z-001/Dataset/Indonesian_Conversational_Speech_Corpus/TXT"
wav_dir = "D:/Buat-kuliah/Semester 7/deep-learning/speech-asr/Dataset-20241216T015426Z-001/Dataset/Indonesian_Conversational_Speech_Corpus/WAV"
output_root = "D:/Buat-kuliah/Semester 7/deep-learning/speech-asr/Dataset-20241216T015426Z-001/Dataset/test-indonesia"

# Parse SPKINFO.txt
def parse_spkinfo(filepath):
    speakers = {}
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("CHANNEL"):
                fields = line.split()
                if len(fields) >= 6:
                    speaker_id = fields[1].strip()
                    speakers[speaker_id] = {
                        "gender": fields[2].strip(),
                        "age": fields[3].strip(),
                        "region": fields[4].strip(),
                        "device": fields[5].strip(),
                    }
                else:
                    print(f"Skipping malformed line: {line}")
    return speakers

# Parse TXT files to extract utterance details
def parse_txt_file(txt_file):
    utterances = []
    with open(txt_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                fields = line.split(maxsplit=3)  # Extract [start_time, end_time, speaker_id, transcript]
                if len(fields) >= 4:
                    start_time, end_time = map(float, fields[0].strip("[]").split(","))
                    speaker_id = fields[1].strip()
                    transcript = fields[3].strip()

                    # Skip non-speech entries
                    if speaker_id == "0":
                        print(f"Skipping non-speech entry: {line}")
                        continue
                    if transcript in ["[*]", "[LAUGHTER]", "[SONANT]", "[MUSIC]", "[SYSTEM]", "[ENS]"]:
                        print(f"Skipping noise transcript: {line}")
                        continue

                    # Add valid utterance
                    utterances.append({
                        "start_time": start_time,
                        "end_time": end_time,
                        "speaker_id": speaker_id,
                        "transcript": transcript,
                    })
    return utterances


# Split audio files and restructure dataset
def segment_and_restructure(txt_dir, wav_dir, output_root):
    if not os.path.exists(output_root):
        os.makedirs(output_root)

    for txt_file in os.listdir(txt_dir):
        if txt_file.endswith(".txt"):
            txt_path = os.path.join(txt_dir, txt_file)
            utterances = parse_txt_file(txt_path)

            # Extract corresponding WAV file
            wav_file = os.path.splitext(txt_file)[0] + ".wav"
            wav_path = os.path.join(wav_dir, wav_file)
            if not os.path.exists(wav_path):
                print(f"Missing audio file: {wav_path}")
                continue

            audio = AudioSegment.from_wav(wav_path)
            for i, utt in enumerate(utterances):
                speaker_id = utt["speaker_id"]
                start_ms = int(utt["start_time"] * 1000)  # Convert to milliseconds
                end_ms = int(utt["end_time"] * 1000)      # Convert to milliseconds

                # Create speaker directory
                speaker_dir = os.path.join(output_root, speaker_id)
                if not os.path.exists(speaker_dir):
                    os.makedirs(speaker_dir)

                # Create chapter directory (using "0001" since there's no chapter info)
                chapter_dir = os.path.join(speaker_dir, "0001")
                if not os.path.exists(chapter_dir):
                    os.makedirs(chapter_dir)

                # Extract and save utterance
                utterance_audio = audio[start_ms:end_ms]
                utt_id = f"{speaker_id}-0001-{str(i).zfill(4)}.wav"
                utt_path = os.path.join(chapter_dir, utt_id)
                utterance_audio.export(utt_path, format="wav")

                # Write transcription
                trans_file = os.path.join(chapter_dir, f"{speaker_id}-0001.trans.txt")
                with open(trans_file, "a") as trans_f:
                    trans_f.write(f"{os.path.splitext(utt_id)[0]} {utt['transcript']}\n")

# Main execution
if __name__ == "__main__":
    speakers = parse_spkinfo(spkinfo_path)
    print(f"Parsed {len(speakers)} speakers")
    segment_and_restructure(txt_dir, wav_dir, output_root)
    print(f"Dataset reorganized successfully into {output_root}.")
