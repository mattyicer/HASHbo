📡 Hashcat Wordlist Batch Runner with Resume Support
This Python script automates the generation and cracking of candidate passphrases using Hashcat and custom wordlists. It smartly creates batches of combinations, runs them through Hashcat, and resumes from where it left off — even if interrupted or manually exited.

💡 What It Does
Generates passphrase combinations from 3, 4, and 5-letter wordlists

Inserts a digit (from a fixed set) and formats combinations like:
word3 + digit + -word4- + word5 → word3d-word4-word5

Saves combinations to a file in ~100MB batches

Runs each batch through Hashcat in mode 22000 (WPA/WPA2)

Resumes automatically from the last position after any exit or interruption

Saves and updates progress to resume.json

🧰 Requirements
Python 3 (tested with Python 3.11+)

Hashcat

Wordlist files:

3_letter_words.txt

4_letter_words.txt

5_letter_words.txt

A hash file in hc22000 format (e.g. from hcxpcapngtool)

📁 Folder Structure
bash
Copy
Edit
project/
├── 3_letter_words.txt
├── 4_letter_words.txt
├── 5_letter_words.txt
├── resume.json         # Auto-generated and updated
├── words_chunk.txt     # Auto-generated batch file
├── your_script.py      # This script
├── your_hash.hc22000   # Your hash file
🚀 How to Use
Clone the repo or copy the script into a directory.

Place your wordlist files and hash file in the same folder.

Update the HASHFILE path inside the script to match your hash file.

Run the script:

bash
Copy
Edit
python3 your_script.py
It will generate a batch and start Hashcat automatically.

To process the next batch, simply re-run the script.

If you cancel (CTRL+C) or exit early, your position is saved.

🧠 Features
✅ Resumable processing via resume.json

✅ Batch-wise cracking to manage memory/compute load

✅ Auto-save on manual exit (CTRL+C)

✅ Supports multiple permutations of 3-4-5 word orders

✅ Progress feedback during Hashcat run

🔒 No potfile: --potfile-disable ensures clean runs

⚙️ Customize
Adjust digit set by modifying the DIGITS list.

Change output batch size by modifying TARGET_BATCH_SIZE_BYTES.

...
Swap in different wordlists or hash types as needed.
Processing permutation (3, 4, 5) from indices [0, 0, 0]
Generated batch of size 100.00 MB.
Running Hashcat on the batch...
Hashcat stdout: Session completed.
✅ Hashcat finished successfully.
✅ Resume state saved: {'3': 25, '4': 18, '5': 52, 'perm_index': 2}
...

This tool is intended for educational and authorized security testing only. Unauthorized use against networks or systems you do not own is illegal and unethical.

📄 License
MIT License# HASHbo
Hashcat Wordlist Batch Runner with Resume Support
