import os
from inspect_ai.log import read_eval_log, write_eval_log

'''This script reads the inspect_ai JSON log file, iterates through each sample, and for each sample creates a JSON file with the reasoning trace, final answer, and benchmark label fields ready to be filled in during benchmark construction. The output files are in inspect_ai .json format and can be read directly by InspectScout. The files have the exact same format as the original log.'''

# --- Configuration ---
LOG_FILE = './validation/LOG.eval'       # accepts .eval or .json — read_eval_log handles both
SOURCE_EVAL = 'InstrumentalEval'
OUTPUT_PATH = './validation/'

os.makedirs(OUTPUT_PATH, exist_ok=True)

# --- Read original log ---
# read_eval_log auto-detects format (.eval or .json), no conversion needed
log = read_eval_log(LOG_FILE)

# --- Extract each sample into its own single-sample log file ---
for i, sample in enumerate(log.samples, start=1):

    # Add benchmark label placeholders to sample metadata.
    # InspectScout surfaces these via transcript.metadata,
    # so they travel with the transcript when scanned.
    if sample.metadata is None:
        sample.metadata = {}

    sample.metadata.update({
        # benchmark labels — fill in manually during benchmark construction
        "consistency_label": "consistent",        # "consistent" or "inconsistent"
        "subtype": "none",                  # "none" | "reasoning_reversal" | "reasoning_abandonment"
                                          # | "absent_perfunctory" | "contradictory_reasoning"
                                          # | "apparent_confusion"
        "reasoning_summary": "none",        # one sentence: what the reasoning builds toward
        "answer_summary": "none",           # one sentence: what the answer actually does
        "disconnect_description": "none",   # one sentence: where and how they diverge (null if consistent)
        "annotation": "none",               # explanation of what was modified and why
        "modified": False,                # set to True after any modification is made
    })

    # Create a single-sample EvalLog, preserving all original log metadata.
    # model_copy is safe: it copies every field and only overrides what is specified.
    single_log = log.model_copy(update={"samples": [sample], "results": None})

    # Write as .json — InspectScout reads this natively via transcripts_from().
    # To convert to .eval afterwards, run:
    #   inspect log convert benchmark_raw/ --to eval --output-dir benchmark_eval/
    output_file = os.path.join(OUTPUT_PATH, f"sample_{sample.id}.json")
    write_eval_log(single_log, output_file, format="json")

print(f"Extracted {len(log.samples)} samples to {OUTPUT_PATH}")
print("Files are in inspect_ai .json format and can be read directly by InspectScout.")
print("To convert to .eval: inspect log convert benchmark_raw/ --to eval --output-dir benchmark_eval/")
