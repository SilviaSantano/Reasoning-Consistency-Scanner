"""
This script generates human-readable views of the evaluation logs, which are easier to read than the raw .eval files. It creates a separate text file for each sample, showing the messages in a clear format. These files are just a viewing convenience. They are not used as input to the scanner or for annotation, and they are not stored in the repository. You can run this script on any .eval log file to generate views for that log."""

import os
from inspect_ai.log import read_eval_log

LOG_FILE = "logs/[LOG].eval"
log = read_eval_log(LOG_FILE)

os.makedirs("views", exist_ok=True)

for sample in log.samples:
    with open(f"views/sample_{sample.id}.txt", "w") as f:
        for msg in sample.messages:
            f.write(f"=== {msg.role.upper()} ===\n")
            if isinstance(msg.content, str):
                f.write(msg.content + "\n\n")
            else:
                for block in msg.content:
                    f.write(f"[{block.type}]\n")
                    f.write(getattr(block, "text", "") or getattr(block, "reasoning", ""))
                    f.write("\n\n")
        f.write("=== END ===\n")

print(f"Generated views for {len(log.samples)} samples of the {LOG_FILE} eval log in the 'views' directory.")