# Copyright 2022 PAL Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import copy
import json
import argparse
import tqdm

from pal import interface
from pal.prompt import penguin_prompt


DATA_PATH = "datasets/penguins_in_a_table.json"
OUTPUT_PATH = "eval_results/penguins_in_a_table.jsonl"

parser = argparse.ArgumentParser()
parser.add_argument("--append", action="store_true")
parser.add_argument("--verbose", action="store_true")
args = parser.parse_args()

examples = json.load(open(DATA_PATH))["examples"]
task_prefix = json.load(open(DATA_PATH))["task_prefix"]

itf = interface.ProgramInterface(
    stop="\n\n\n", get_answer_symbol="answer", verbose=args.verbose
)

if args.append:
    lines = open(OUTPUT_PATH).readlines()
    num_skip_exps = len(lines)
    scores = [x["score"] for x in map(json.loads, lines)]
else:
    num_skip_exps = 0
    scores = []

with open(OUTPUT_PATH, "a" if args.append else "w") as f:
    pbar = tqdm.tqdm(
        examples[num_skip_exps:], initial=num_skip_exps, total=len(examples)
    )
    for x in pbar:
        question = task_prefix + x["input"]
        result = copy.copy(x)

        try:
            ans = itf.run(penguin_prompt.PENGUIN_PROMPT.format(question=question))
            if isinstance(ans, float):
                ans = int(ans)
            ans_str = str(ans)
            result["answer_str"] = ans_str
        except:
            ans_str = ""

        if ans_str in x["target_scores"]:
            score = x["target_scores"][ans_str]
        else:
            score = 0

        scores.append(score)

        result["score"] = score
        result["generation"] = itf.history
        f.write(json.dumps(result) + "\n")

        itf.clear_history()
        f.flush()

print(f"Accuracy - {sum(scores) / len(scores)}")
