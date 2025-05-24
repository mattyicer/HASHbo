#!/opt/homebrew/bin/python3

import json
import os
import time
import signal
import atexit
from itertools import permutations
import subprocess
import sys

# Configurations
WORDLISTS = {
    3: "3_letter_words.txt",
    4: "4_letter_words.txt",
    5: "5_letter_words.txt"
}
RESUME_FILE = "resume.json"
HASHFILE = "/path/to/yourfile/your_hash_file.hc22000"
DIGITS = ['3', '4', '6', '7', '9']
HASHCAT_MODE = "22000"
TARGET_BATCH_SIZE_BYTES = 100 * 1024 * 1024  # 100MB

# Global state for cleanup
global_state = {
    "words": None,
    "state": None,
    "last_candidate_info": None
}

def load_words():
    print("Loading word lists...")
    words = {}
    for k, filename in WORDLISTS.items():
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Missing wordlist file: {filename}")
        with open(filename) as f:
            words[k] = [line.strip() for line in f]
        print(f"Loaded {len(words[k])} words for {k}-letter list.")
    return words

def load_state():
    if os.path.exists(RESUME_FILE):
        with open(RESUME_FILE) as f:
            state = json.load(f)
        print(f"Loaded resume state: {state}")
    else:
        state = {'3': 0, '4': 0, '5': 0, 'perm_index': 0}
        print("No resume file found, starting from scratch.")
    return state

def save_state(state, last_candidate_info=None):
    if last_candidate_info:
        p_i, o1, i1, o2, i2, o3, i3 = last_candidate_info
        state['perm_index'] = p_i
        state[str(o1)] = i1 + 1
        state[str(o2)] = i2
        state[str(o3)] = i3
        print(f"✅ Resume data updated from last candidate: {last_candidate_info}")
    with open(RESUME_FILE, 'w') as f:
        json.dump(state, f)
    print(f"✅ Resume state saved: {state}")

# Ensure resume is saved on exit
def handle_exit():
    state = global_state.get("state")
    last_info = global_state.get("last_candidate_info")
    if state and last_info:
        print("\n🔁 Saving resume state before exit...")
        save_state(state, last_info)

# Register exit handlers
atexit.register(handle_exit)
signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
signal.signal(signal.SIGTERM, lambda sig, frame: sys.exit(0))

PERMUTATIONS = list(permutations([3, 4, 5]))

def generate_candidates(words, state):
    perm_idx = state.get('perm_index', 0)
    for p_i in range(perm_idx, len(PERMUTATIONS)):
        order = PERMUTATIONS[p_i]
        w1_list, w2_list, w3_list = [words[o] for o in order]
        s_indices = [state.get(str(order[0]), 0),
                     state.get(str(order[1]), 0),
                     state.get(str(order[2]), 0)]

        i1_start, i2_start, i3_start = s_indices
        print(f"Processing permutation {order} from indices {s_indices}")

        for i1 in range(i1_start, len(w1_list)):
            for i2 in range(i2_start if i1 == i1_start else 0, len(w2_list)):
                for i3 in range(i3_start if i1 == i1_start and i2 == i2_start else 0, len(w3_list)):
                    for d in DIGITS:
                        candidate = f"{w1_list[i1]}{d}-{w2_list[i2]}-{w3_list[i3]}"
                        yield candidate, (p_i, order[0], i1, order[1], i2, order[2], i3)

def run_hashcat_with_progress(args):
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    start_time = time.time()
    while True:
        ret = proc.poll()
        elapsed = int(time.time() - start_time)
        for line in proc.stdout:
            print("Hashcat stdout:", line.strip())
        for line in proc.stderr:
            print("Hashcat stderr:", line.strip())
        if ret is not None:
            return ret
        if elapsed % 10 == 0:
            print(f"Hashcat running... elapsed {elapsed} seconds")
        time.sleep(1)

def main():
    print("\n=== Starting the script ===")
    words = load_words()
    state = load_state()
    global_state["words"] = words
    global_state["state"] = state

    print(f"\n=== Generating next batch (~{TARGET_BATCH_SIZE_BYTES // (1024*1024)}MB) ===")
    filename = "words_chunk.txt"
    bytes_written = 0

    with open(filename, "w") as f:
        for candidate, info in generate_candidates(words, state):
            f.write(candidate + "\n")
            bytes_written += len(candidate) + 1
            global_state["last_candidate_info"] = info
            if bytes_written >= TARGET_BATCH_SIZE_BYTES:
                break

    if bytes_written == 0:
        print("✅ No more candidates to generate. All permutations processed.")
        return

    print(f"Generated batch of size {bytes_written / (1024**2):.2f} MB.")
    print("Running Hashcat on the batch...")

    retcode = run_hashcat_with_progress([
        "hashcat", "-m", HASHCAT_MODE, "-a", "0", "--remove", "--force",
        HASHFILE, filename
    ])

    if retcode != 0:
        print(f"❌ Hashcat exited with code {retcode}.")
    else:
        print("✅ Hashcat finished successfully.")

    print("\n✅ Done for now. Re-run the script to process the next batch.")

if __name__ == "__main__":
    main()
