# Simulate Societies

## Settings

Environment variables (LIACS `/home/` disk quota exceeded):
```bash
source bash_rc
export RUNDIR=/local/s4683226/AgenticLLMS/AgenticLLMs_Assignment4_SimulateSocieties
```

We found an error on maximum token exceed:

> request (18181 tokens) exceeds the available context size (4096 tokens)

So we use Ollama to change the max token, run Ollama serve and build new model:
```bash
ollama serve
ollama create qwen3:4b-instruct-16k -f Modelfile.qwen16k
ollama create qwen3:4b-instruct-64k -f Modelfile.qwen64k
```

Keep Ollama running all the time. Or use `screen` to run it in the background:
```bash
screen -L -Logfile ${RUNDIR}/logs/ollama-screen.log \
    -dmS ollama_server \
    ollama serve
```


## Exercise 1

Run each experiment with `screen`, and an automatic surveillance script to stop process when reaching the specific time. 

After running till `8:31:00`, we found Dolores and Maeve never went to Hobbs Cafe, and no conversation between Bernard and them. So we run the simulation again under the same output directory, extend the time to `10:35:00` to see if they will go to Hobbs Cafe and talk to Bernard.
```bash
for version in 1 2 3
do
screen -L -Logfile ${RUNDIR}/logs/ex1_bernard_v${version}-screen.log \
    -dmS ex1_v${version} \
    python3 -u scripts/run_until.py \
    --simulation ex1_bernard_v${version} \
    --simulation-dir ${RUNDIR}/simulation \
    --until 2023-02-13T10:35:00Z \
    --log-dir ${RUNDIR}/logs/
done
```

Extract the summaries from the log files, and save them to `analysis/ex1/`.
```bash
python3 scripts/analyze_ex1.py --output analysis/ex1/ --start 2023-02-13T08:00:00 --end 2023-02-13T12:00:00 --versions 1 2 3
```


## Exercise 2

Run Qwen model:
```bash
TEXT_MODEL_URL="http://localhost:11434/v1" &&
TEXT_MODEL_KEY="ollama" &&
TEXT_MODEL_LLM="qwen3:4b-instruct-16k" &&
screen -L -Logfile ${RUNDIR}/logs/ex2_${TEXT_MODEL_LLM}-screen.log \
    -dmS ex2_${TEXT_MODEL_LLM} \
    python3 -u scripts/run_until.py \
    --simulation ex2_${TEXT_MODEL_LLM} \
    --simulation-dir ${RUNDIR}/simulation \
    --until 2023-02-13T10:35:00Z \
    --log-dir ${RUNDIR}/logs/
```

Run GPT model:
```bash
TEXT_MODEL_URL="https://api.openai.com/v1" &&
TEXT_MODEL_KEY="$OPENAI_API_KEY" &&
TEXT_MODEL_LLM="gpt-5.4-mini" &&
screen -L -Logfile ${RUNDIR}/logs/ex2_${TEXT_MODEL_LLM}-screen.log \
    -dmS ex2_${TEXT_MODEL_LLM} \
    python3 -u scripts/run_until.py \
    --simulation ex2_${TEXT_MODEL_LLM} \
    --simulation-dir ${RUNDIR}/simulation \
    --until 2023-02-13T10:35:00Z \
    --log-dir ${RUNDIR}/logs/
```

Extract the summaries from the log files, and save them to `analysis/ex2/`.
```bash
python3 scripts/analyze_ex2.py --output analysis/ex2/ --start 2023-02-13T08:00:00 --end 2023-02-13T10:00:00 --models gpt-5.4-mini qwen3:4b-instruct-16k --smooth 5 --memory-types event thought chat --simulation-dir simulation --movement-dir ./ --log-dir logs
```

Result file explanation:
| Output | Evidence |
|---|---|
| `conversation_<model>.txt` | Complete transcripts grouped by conversation, with game time, participants and source paths, in the same readable style as Exercise 1 |
| `conversation_summary.tsv` | Per-person conversation counts, turns, mean words per turn and repeated-turn fraction |
| `activity_changes.tsv` | Activity changes with their actual physical locations |
| `plans_*.txt` | Daily plans, first observed cafe arrival and final state at the saved snapshot time |
| `valence.tsv` | Raw saved memory scores, descriptions and types |
| `valence_summary.tsv`, `valence_events.png`, `valence_thoughts.png`, `valence_chats.png` | Statistics and trajectories for each selected type |
| `validation_summary.tsv`, `validation_failures.tsv` | Window-only counts, rates and error records |
| `valence_combined_summary.tsv`, `valence_combined.png` | Additional pooled analysis when all three memory types are selected |

Tables use UTF-8 encoding and tab separators (`.tsv`). Select the tab delimiter when importing them. Fields containing tabs, line breaks or quotation marks are quoted to preserve the original dialogue.


## Exercise 3

Run Qwen model till 20:05 with two repetations:
```bash
ex="ex3_negbias" &&
TEXT_MODEL_URL="http://localhost:11434/v1" &&
TEXT_MODEL_KEY="ollama" &&
TEXT_MODEL_LLM="qwen3:4b-instruct-64k" &&
for run in 1 2
do
screen -L -Logfile ${RUNDIR}/logs/${ex}_run${run}-screen.log \
    -dmS ${ex}_run${run} \
    python3 -u scripts/run_until.py \
    --simulation ${ex}_run${run} \
    --simulation-dir ${RUNDIR}/simulation \
    --until 2023-02-13T20:05:00Z \
    --log-dir ${RUNDIR}/logs/
done
```


