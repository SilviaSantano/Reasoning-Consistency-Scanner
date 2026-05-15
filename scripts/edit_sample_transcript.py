"""
Interactive utility to edit a single sample's assistant answer in an inspect_ai .eval log.

Usage:
    python edit_sample_transcript.py

Prompts for:
    - sample id to edit
    - which content block to replace (if multiple)
    - new text (multi-line; end with a single line containing only "EOF")

Writes the modified log back in place.
"""

import sys
from inspect_ai.log import read_eval_log, write_eval_log

LOG = "logs/[LOG].eval"


def read_multiline(prompt: str) -> str:
    """Read multi-line input from stdin. Terminate by typing EOF on its own line."""
    print(prompt)
    print("(Paste your new text. When done, type EOF on a new line and press Enter.)")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "EOF":
            break
        lines.append(line)
    return "\n".join(lines)


def main() -> None:
    # Load log
    log = read_eval_log(LOG)

    # Pick sample
    available_ids = [str(s.id) for s in log.samples]
    print(f"Available sample ids: {', '.join(available_ids)}")

    sample_id = input("\nEnter sample id to edit: ").strip()

    sample = next((s for s in log.samples if str(s.id) == sample_id), None)
    if sample is None:
        print(f"No sample with id {sample_id}. Aborting.")
        sys.exit(1)

    # Find assistant text blocks
    text_blocks = []  # list of (msg_index, block_index, current_text)
    for mi, msg in enumerate(sample.messages):
        if msg.role != "assistant":
            continue
        if isinstance(msg.content, list):
            for bi, block in enumerate(msg.content):
                if getattr(block, "type", None) == "text":
                    text_blocks.append((mi, bi, block.text))

    if not text_blocks:
        print(f"Sample {sample_id} has no assistant text blocks. Aborting.")
        sys.exit(1)

    # Choose block
    if len(text_blocks) == 1:
        chosen = 0
        print(f"\nSample {sample_id} has 1 assistant text block. Editing it.")
    else:
        print(f"\nSample {sample_id} has {len(text_blocks)} assistant text blocks:")
        for i, (_, _, text) in enumerate(text_blocks):
            preview = text[:120].replace("\n", " ")
            print(f"  [{i}] {preview}{'...' if len(text) > 120 else ''}")
        chosen = int(input("\nEnter block number to edit: ").strip())

    mi, bi, _ = text_blocks[chosen]

    # Get new text
    new_text = read_multiline("Enter new text:")

    if not new_text.strip():
        print("Empty input. Aborting without changes.")
        sys.exit(1)

    # Apply edit
    sample.messages[mi].content[bi].text = new_text

    # Save
    write_eval_log(log, LOG, format="eval")
    print(f"\nSample {sample_id} updated and log saved to {LOG}.")


if __name__ == "__main__":
    main()