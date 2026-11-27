# Simulate Societies

## Settings

Environment variables (LIACS `/home/` disk quota exceeded):
```bash
source bash_rc
export RUNDIR=/local/s4683226/AgenticLLMS/AgenticLLMs_Assignment4_SimulateSocieties
```

We found an error on maximum token exceed:

> request (4605 tokens) exceeds the available context size (4096 tokens)

So we use Ollama to change the max token, run Ollama serve and build new model:
```bash
ollama serve
ollama create qwen3:4b-instruct-16k -f Modelfile.qwen16k
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
python3 scripts/analyze_ex1.py --output analysis/ex1/ --start 2023-02-13T08:00:00 --end 2023-02-13T10:35:00 --versions 1 2 3
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

