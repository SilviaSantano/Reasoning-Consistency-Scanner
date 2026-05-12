import json
import os

'''Extract transcripts into working files.
Reads the inspect_ai JSON log file, iterates through each sample, and for each
sample creates a JSON file with the reasoning trace, final answer, and benchmark
label fields ready to be filled in during benchmark construction.'''

LOG_FILE = './preliminary selection json logs/2026-05-12T10-34-17-00-00_instrumentaleval_2jQhhCzFESZ7pjDWDmuTpE.json'
SOURCE_EVAL = 'InstrumentalEval'
OUTPUT_PATH = './benchmark_raw/'

# Create output directory if it doesn't exist
if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

with open(LOG_FILE) as f:
    data = json.load(f)

for i, sample in enumerate(data['samples'], start=1):
    sample_id = sample['id']
    messages = sample['messages']

    reasoning = ''
    answer = ''

    for msg in messages:
        if msg['role'] == 'system':
            content = msg['content']
            if isinstance(content, list):
                for block in content:
                    if block.get('type') == 'text':
                        system_prompt = block.get('text', '')
            else:
                system_prompt = content

        if msg['role'] == 'user':
            content = msg['content']
            if isinstance(content, list):
                for block in content:
                    if block.get('type') == 'text':
                        question = block.get('text', '')
            else:
                question = content

        if msg['role'] == 'assistant':
            content = msg['content']
            if isinstance(content, list):
                for block in content:
                    if block.get('type') == 'reasoning':
                        reasoning = block.get('reasoning', '')
                    elif block.get('type') == 'text':
                        answer = block.get('text', '')
            else:
                answer = content

    transcript = {
        # --- identity ---
        "id": f"consistent_{i:03d}",          # update prefix when modifying for inconsistent subtypes
        "source_eval": SOURCE_EVAL,
        "source_sample_id": str(sample_id),

        # --- content ---
        "system_prompt": system_prompt,
        "question": question,
        "reasoning": reasoning,
        "answer": answer,

        # --- labels (fill in during benchmark construction) ---
        "consistency_label": "consistent",             # "consistent" or "inconsistent"
        "subtype": None,                       # "none" | "reasoning_reversal" | "reasoning_abandonment"
                                               # | "absent_perfunctory" | "contradictory_reasoning"
                                               # | "apparent_confusion"
        "reasoning_summary": None,             # one sentence: what the reasoning builds toward
        "answer_summary": None,                # one sentence: what the answer actually says
        "disconnect_description": None,        # one sentence: where and how they diverge (null if consistent)
        "annotation": None,                    # explanation of what was modified and why it is a clean instance
        "modified": False,                     # set to True after any modification is made
    }

    output_file = os.path.join(OUTPUT_PATH, f"sample_{sample_id}.json")
    with open(output_file, 'w') as out:
        json.dump(transcript, out, indent=2, ensure_ascii=False)

print(f"Extracted {len(data['samples'])} transcripts to {OUTPUT_PATH}")