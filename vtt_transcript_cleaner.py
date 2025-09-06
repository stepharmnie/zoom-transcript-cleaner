# This python script walks through all the folders in the "Recordings and transcripts" folder, finds the vtt, and then cleans it up to make it more readable


import os
import re
import shutil

# === Configuration ===
# Edit these paths in the script:
base_dir = '/Path/to/Recordings and zoom transcripts/unprocessed'
processed_dir = '/Path/to/Recordings and zoom transcripts/processed'  
output_base_dir = '/Path/to/Recordings and zoom transcripts/converted_txt'
os.makedirs(output_base_dir, exist_ok=True)

def convert_structured_vtt_to_txt(vtt_path, txt_path):
    with open(vtt_path, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file if line.strip()]

    output_lines = []
    current_speaker = None
    current_text = []

    i = 0
    while i < len(lines):
        # Skip entry number
        if lines[i].isdigit():
            i += 1
            continue

        # Skip timestamp
        if re.match(r"\d{2}:\d{2}:\d{2}\.\d{3} -->", lines[i]): 
            i += 1
            continue

        # Expect: "speaker name: text"
        line = lines[i]
        i += 1

        match = re.match(r"([^:]+):\s*(.+)", line)
        if match:
            speaker = match.group(1).strip()
            text = match.group(2).strip()

            if speaker == current_speaker:
                current_text.append(text)
            else:
                # Flush previous speaker
                if current_speaker and current_text:
                    combined = ' '.join(current_text)
                    output_lines.append(f"{current_speaker}: {combined}")
                current_speaker = speaker
                current_text = [text]

    # Flush last speaker
    if current_speaker and current_text:
        combined = ' '.join(current_text)
        output_lines.append(f"{current_speaker}: {combined}")

    # Write to txt
    with open(txt_path, 'w', encoding='utf-8-sig') as out:
        for line in output_lines:
            out.write(line + '\n\n')

    print(f"Saved: {txt_path}")

# === Usage ===
for folder_name in sorted(os.listdir(base_dir)):
    folder_path = os.path.join(base_dir, folder_name)
    if os.path.isdir(folder_path):
        vtt_file_found = False
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(".vtt"):
                vtt_path = os.path.join(folder_path, filename)
                
                # Name the output .txt file based on folder + original name
                txt_filename = f"{folder_name}_{os.path.splitext(filename)[0]}.txt"
                txt_path = os.path.join(output_base_dir, txt_filename)

                convert_structured_vtt_to_txt(vtt_path, txt_path)
                vtt_file_found = True
        # move folder for each recording to "processed" folder
        if vtt_file_found:
            shutil.move(folder_path, processed_dir)
print("All VTT files converted")
