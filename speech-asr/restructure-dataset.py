import os
import shutil

# File paths (adjust as needed)
spkinfo_path = "D:/Buat-kuliah/Semester 7/deep-learning/speech-asr/Dataset-20241216T015426Z-001/Dataset/Indonesian_Scripted_Speech_Corpus_Daily_Use_Sentence/SPKINFO.txt"
uttransinfo_path = "D:/Buat-kuliah/Semester 7/deep-learning/speech-asr/Dataset-20241216T015426Z-001/Dataset/Indonesian_Scripted_Speech_Corpus_Daily_Use_Sentence/UTTRANSINFO.txt"
wav_root = "D:/Buat-kuliah/Semester 7/deep-learning/speech-asr/Dataset-20241216T015426Z-001/Dataset/Indonesian_Scripted_Speech_Corpus_Daily_Use_Sentence/WAV"
output_root = "D:/Buat-kuliah/Semester 7/deep-learning/speech-asr/Dataset-20241216T015426Z-001/Dataset/train-indonesia"

# Step 1: Parse SPKINFO.txt
def parse_spkinfo(filepath):
    speakers = {}
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and header
            if line and not line.startswith("#") and not line.startswith("CHANNEL"):
                # Split on any whitespace
                fields = line.split()
                if len(fields) >= 6:  # Ensure all columns are present
                    speaker_id = fields[1].strip()  # SPEAKER_ID
                    speakers[speaker_id] = {
                        "gender": fields[2].strip(),
                        "age": fields[3].strip(),
                        "region": fields[4].strip(),
                        "device": fields[5].strip(),
                    }
                else:
                    print(f"Skipping malformed line: {line}")
    return speakers

# Step 2: Parse UTTRANSINFO.txt
def parse_uttransinfo(filepath):
    """Parse UTTRANSINFO.txt to extract utterance details."""
    utterances = {}
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and headers
            if line and not line.startswith("#") and not line.startswith("CHANNEL"):
                fields = line.split(maxsplit=4)  # Split into at most 5 parts
                if len(fields) >= 5:  # Ensure all necessary fields are present
                    file_path = fields[1].strip()  # UTTRANS_ID
                    speaker_id = fields[2].strip()  # SPEAKER_ID
                    transcription = fields[4].strip()  # TRANSCRIPTION
                    utterances[file_path] = {
                        "speaker_id": speaker_id,
                        "transcription": transcription,
                    }
                else:
                    print(f"Skipping malformed line: {line}")
    return utterances

# Step 3: Reorganize files
def reorganize_files(speakers, utterances, wav_root, output_root):
    if not os.path.exists(output_root):
        os.makedirs(output_root)

    for file_path, data in utterances.items():
        speaker_id = data["speaker_id"]
        transcription = data["transcription"]

        # Create speaker directory
        speaker_dir = os.path.join(output_root, speaker_id)
        if not os.path.exists(speaker_dir):
            os.makedirs(speaker_dir)

        # Create chapter directory (using "0001" since there's no chapter info)
        chapter_dir = os.path.join(speaker_dir, "0001")
        if not os.path.exists(chapter_dir):
            os.makedirs(chapter_dir)

        # Copy audio file
        src_audio_path = os.path.join(wav_root, speaker_id, file_path)
        filename = f"{speaker_id}-0001-{os.path.splitext(os.path.basename(file_path))[0]}.wav"
        dest_audio_path = os.path.join(chapter_dir, filename)
        if os.path.exists(src_audio_path):
            shutil.copyfile(src_audio_path, dest_audio_path)

        # Write transcription
        trans_file = os.path.join(chapter_dir, f"{speaker_id}-0001.trans.txt")
        with open(trans_file, "a") as trans_f:
            trans_f.write(f"{os.path.splitext(filename)[0]} {transcription}\n")

# Main execution
if __name__ == "__main__":
    speakers = parse_spkinfo(spkinfo_path)
    utterances = parse_uttransinfo(uttransinfo_path)
    print(f"Parsed {len(utterances)} utterances")
    reorganize_files(speakers, utterances, wav_root, output_root)

    print(f"Dataset reorganized successfully into {output_root}.")
