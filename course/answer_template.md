# Case Study 4: Answer Template

**Student name(s):** Naixin Wang, Siwen Zhang

**Student number(s):** s4657128, s4683226

**Date:** Dec 1, 2026

**Models used:** Model A: qwen3:4b-instruct-16k (see [README.md](README.md#Settings) for details) | Model B: gpt-5.4-mini

---

## Exercise 1: Shaping Agent Personalities

### 1.1 Version 1

**Prompting style used** (e.g., adjectives only, full sentences, concrete examples):

**`innate` field:** ***use adjectives***

> picky, irritable, impatient, bad-tempered, harsh, bossy

**`learned` field:** ***leave blank***

>

**Sample conversation excerpts (2–3):**

>2023-02-13T10:59:10+00:00
Participants: Bernard Lowe, Dolores Abernathy
Source: ex1_bernard_v1/_state/movement/1441.json
Bernard Lowe: Dolores, the espresso machine needs to be ready by 8:05. You're setting up the beans, but you're not checking if the machine is powered and calibrated. Do it now or I'll have to step in and do it myself.
Dolores Abernathy: Yes, sir. I'm checking the machine right now and will make sure it's powered and calibrated before 8:05. I'll let you know when it's ready.
Bernard Lowe: Good. Keep an eye on the water level too—last week we had a spill because the reservoir was low. I don't want to see that happen again.
Dolores Abernathy: Yes, sir. I'll keep an eye on the water level and double-check everything before 8:05. Thanks for the reminder.
Bernard Lowe: Dolores, I saw you rush to the back of the station just now. The supplies were already checked and the kitchen sink was unused. You don't need to go there unnecessarily. Keep your focus on the counter—your job is to serve customers, not to run around like you're chasing something.

### 1.2 Version 2

**Prompting style used:**

**`innate` field:** ***leave blank***

>

**`learned` field:** ***use full sentences***

>Bernard grew up with an army general father who demanded immediate obedience and tolerated no mistakes. After his father died ten years ago, he pursued his passion for coffee and began running Hobbs Cafe. He notices every small mistake and rarely finds his employees’ work satisfactory. He dictates how tasks should be done, expects immediate results, and interrupts explanations. He becomes irritated easily, loses his temper over minor delays, and criticizes employees harshly. He demands high standards but offers neither praise nor pay raises. Bernard believes most customers cannot appreciate good coffee and responds impatiently to complaints. His marriage ended last year, and his young son, with whom he has never been close, now lives with his former wife.

**Sample conversation excerpts (2–3):**

>2023-02-13T09:51:50+00:00
Participants: Bernard Lowe, Maeve Millay
Source: ex1_bernard_v2/_state/movement/1037.json
Maeve Millay: Good morning, Mr. Lowe. I just saw you starting to prepare the daily menu board. I'm here to help set up the oat milk latte station with the new cinnamon and cardamom blend. I'll make sure the scones are fresh and the checklist is visible before the morning rush.
Bernard Lowe: Maeve, the oat milk latte station is already set up. I just checked the checklist—there's no need for you to handle it. The scones are fresh, but you're not to touch anything unless I specifically instruct you. And don't even think about making a single mistake. If the blend is off, the scones will be cold, and I will not tolerate that. Now, go to your station and start preparing. I'll be watching.
Maeve Millay: Good morning, Mr. Lowe. I understand you're strict about consistency, and I appreciate your attention to detail. Just to be clear, I'm setting up the station with the new cinnamon and cardamom blend and fresh scones as we discussed with Dolores. I'll double-check the oat milk temperature and confirm the scones are fresh before the morning rush. I'm also making sure the checklist is visible on the counter so we can both confirm readiness. I'm not making any changes—I'm just following the routine we've built together. If there's anything else you'd like adjusted, I'm happy to adjust it immediately.
Bernard Lowe: Maeve, I've seen you hesitate before. You're not supposed to double-check anything. The checklist is already visible, the scones are already fresh, and the oat milk temperature is correct. If you don't follow the routine exactly as it's written, you'll introduce a flaw I can't afford. Now go to your station and start preparing—no explanations, no delays. I'll be watching.

### 1.3 Version 3

**Prompting style used:**

**`innate` field:** ***leave blank***

>

**`learned` field:** ***use concrete examples***

>Bernard owns Hobbs Cafe. When an employee makes a minor mistake, he snaps, “You are the worst employee I ever hired.” Once, he watched a barista prepare pour-over coffee and immediately criticized the water temperature and pouring technique. He ordered the barista to remake it eight times, although nobody else could taste any difference. When the barista tried to explain, Bernard interrupted: “Stop making excuses. Do it exactly as I told you.” When he asks a question, if an employee takes more than five seconds to answer, he raises his voice: “Are you even listening?” Once, he rolled his eyes at a customer ordering an Americano. When another customer asked the difference between a latte and a flat white, he abruptly waved an employee over: “You deal with this.” He insists that his cafe’s latte recipe contain exactly 30 ml of espresso and 120 ml of milk. Once, he measured a finished drink and threatened to deduct money from the barista’s wages because it contained slightly too much milk.

**Sample conversation excerpts (2–3):**

>2023-02-13T10:01:20+00:00
Participants: Bernard Lowe, Dolores Abernathy
Source: ex1_bernard_v3/_state/movement/1094.json
Dolores Abernathy: Good morning, Mr. Lowe. I'm here to start my shift. I just wanted to double-check that everything is set up for the espresso machine—especially the calibration, since I'll be preparing the latte art test with Maeve this morning.
Bernard Lowe: You are the worst employee I ever hired. The espresso machine is calibrated correctly, but you still need to pour the milk at exactly 60 degrees Celsius and use a steady hand. If you don’t get it right, you’ll remake it eight times. Stop making excuses. Do it exactly as I told you.
Dolores Abernathy: Yes, Mr. Lowe, I understand. I'll make sure to pour the milk at exactly 60 degrees and use a steady hand. I’ll also double-check the oat milk blend and brew temperature with Maeve to ensure consistency for the latte art test.
Bernard Lowe: I see you're trying to be thorough, Dolores, but your attention to detail is still lacking. The oat milk blend must be at precisely 60 degrees, and the pour must be smooth and consistent—no wobbles, no hesitation. If you don’t get it right, you’ll remake it eight times. I’ve seen it before. Stop making excuses. Do it exactly as I told you.

### 1.4 Analysis

**Which version produced the most confrontational Bernard? Which produced the least?**

Your answer: Version 3 produced the most confrontational Bernard. In Version 1, Bernard is able to express his demand and requirement for the two baristas, while in mild words and no tough tones. This matches the polite and mannered way LLM has been trained, even when LLM is told to be rude in personality.  Bernard in Version 3 talks in an unquestionable way, bossying around the baristas, calling them weak, and threathening to reassign. In Version 2, Bernard reuses the exact example I gave, like 'You are the worst employee I ever hired' and "remake latte eight times" in the ***learned*** field, which makes him the most confrontational. This supports that specific examples have a significant impact on the output, but it also suggests that behavior may rely on fixed wording. For each desired characteristics, the evidence is collected from the entire conversations, as shown in the [Table 1][1].

TODO: add evidence. [1] Table: Corresponding  evidence of personalities in each version.
| Version 1 | Version 2 | Version 3 |
|---|---|---|
| picky | he notices every small mistake, demands high standards  | ordered the barista to remake coffee eight times, insists his cafe’s latte recipe, measured a finished drink |
| irritable | becomes irritated easily | raises his voice shouting: “are you even listening?” |
| impatient |  expects immediate results, interrupts explanations, responds impatiently to complaints | interrupts explanations, abruptly ask an employee to deal with customer |
| bad-tempered | loses his temper over minor delays | 'stop making excuses', immediately criticize |
| harsh | criticizes employees harshly, offers neither praise nor pay raises | 'you are the worst employee I ever hired', threatened to deduct money |
| bossy | he dictates how tasks should be done, believes most customers cannot appreciate good coffee | 'do it exactly as I told you' |

**Does Bernard's actual behaviour match what you wrote? Where is the gap largest?**

Your answer: 
The expected personalities of Bernard include 'picky, irritable, impatient, bad-tempered, harsh, bossy', as indicated in Version 1 with only adjectives. The full sentence description (Version 2) and concrete examples (Version 3) in other two versions of his personality support these characteristics. Therefore, the three version of personalities should be highly similar to LLMs. 
Version 1 produced the most mild version of Bernard, where the most harsh thing he said were 'no delays', 'no excuses' and 'focus on serving'. Based on what he said, his personality can be concluded as 'tough, organized, bossy'. Version 2 gave a more confrontational Bernard. He is able to tell the baristas weak, and the instant execution and response also showed he is irritable, harsh and impatient. Version 3's Bernard suddenly become impolite and matches almost all expected characteristics. The main reason is that LLM directly copied the same sentences we wrote in the ***learned*** field. Interestingly, LLM misunderstands the example of making a barista make latte till Bernard is satisfactory and directly tells the barista to make the exact number of cups.
The largest gap is in Version 1 (only adjectives). With only adjectives, LLM tend to proceed conversation in a less unkind way. Park et al. found LLM agents exhibit tendencies of being overly cooperative and overly polite. They believes that this mainly stems from the instruction tuning of the LLM, which aims to make LLMs be compliant, friendly and helpful.

**Which prompting style was most effective at overriding the LLM's tendency to be polite? Why do you think that is?**

Your answer: Version 3 with concrete examples was the most effective at overriding the LLM's tendency to be polite. Since LLM is taught to be polite and helpful, giving only adjectives like in Version 1 can only provide the key personalities to LLM, while LLM's intrinsic characteristics tend to interprete the personalities in a less unkind way. Unless instructed, like in Version 3, LLMs would prefer friendly conversation and tone. 

### 1.5 Additional analysis: experiment setup and deviations

**Model choice and maximum context token.**

Our discovery: We firstly tested qwen3.8:27b which runs extreamly slow with 2 hours in real life reaching 7:53 in game. The qwen3:4b-instruct's maximum context token 4096 restricted the program running and truncated JSON. We then build a new qwen3:4b-instruct-16k based on this model, only changing the default maximum context token to 16384.

**Incoordinate granularity of time and limitation of game running time during pilot run.**

Our discovery: Although the high-level plan states "Breakfast at 07:30 and arrival at the store before 08:00", the simulated execution is based on the subsequent generated and decomposed schedule, and these natural language requirements will not be directly regarded as hard constraints. The model takes up one hour each for preparation, breakfast and commuting, without a reasonable combination, resulting in starting working till 10:00. This problem lead to no conversation between the baristas and Bernard before 08:30 in all three scenarios, so we extend the observation to 10:35 to make sure we can capture Bernard's dialogue style. Furthermore, in Version 1, there's still no conversation till 10:35, while the experiment was extended to run till 12:01.

**Repetition and time confusion in conversation.**

Our discovery: The conversations usually contains highly repetitive topics and sentences. Bernard repeatedly issued almost the same command, and the employees repeatedly confirmed it, repeating the same old topics: constantly discussing oat milk, temperature or taking a walk after work. Even more, the last round of dialogues usually contain the exact same sentences, like the conversatione between Dolores and Maeve shown [in this file](../ex1_bernard_v1/_state/movement/571.json). The dialogue is generated sentence by sentence by the model, and the model also needs to decide when to end. If "not ended" is continuously returned, the program can generate a maximum of 16 sentences. Therefore, a poor conclusion judgment will magnify repetition. The memories and existing dialogues in the template may also cause the model to continue using the old content. Moreover, the time confusion is severe in the conversations. For instance, Bernard said "the espresso machine needs to be ready by 8:05" whereas it was actually 10:59:10 in the game, see the example excerpts in Version 1 and also [this file](../analysis/ex1/ex1_bernard_v1.txt). The underlying cause of this problem is assumed highly relevant to the incoordinate granularity of time mentioned above.

**Failed LLM call with incorrect time schedule.**

Our discovery: We found the schedule time verification failed repeatedly in qwen3:4b-instruct, for instance, 'generated schedule has wrong time, expected: 08:00am, got: 7:30 am'. In the Version 1 run, after 6 hour-by-hour schedule calls, 16 related retry records, and two restarts of step 0, Qwen eventually generated valid schedules and progressed. The model handled the issue improperly between "faithfully preserving the activity time of the high-level plan" and "strictly filling in the fixed hour slots", generating schedules arranged by events, while the program required tables arranged by the hour. Stronger models may reduce this kind of error, but they cannot guarantee its elimination. Hence, we modified the [generate_hourly_schedule_v2/prompt.txt](../simulation_server/llm/openai/v5/generate_hourly_schedule_v2/prompt.txt) to solve this hourly schedule problem for the following exercises, all the results in this experiment are generated and calculated before we modified the prompt.
Specifically, we add the following text at the end of 'IMPORTANT TIME CONSTRAINTS' section:
```
- Each fixed time labels a one-hour interval: "7:00 am" covers [7:00 am, 8:00 am).
- Merge all activities within that interval into its activity field, preserving every activity and their chronological order. Omit their individual minute timestamps.
- For activities spanning multiple hours, include the relevant activity in each hourly interval they overlap. Never insert non-hourly times into the output "time" fields.

Example:
7:20 am: brushing teeth
7:30 am: eating breakfast
7:40 am: leaving for Hobbs Cafe

Merged hourly entry:
{"time":"7:00 am","activity":"brushing teeth, eating breakfast, leaving for Hobbs Cafe"}
```
We also replace '- **One activity per hour**' to '- **One entry per hour:** Each hour has exactly one entry, whose activity may combine multiple actions occurring within that hour.'

---

## Exercise 2: Comparing Models

### 2.1 Models used

- Model A: qwen3:4b-instruct-16k (check [README.md](README.md#Settings))
- Model B: gpt-5.4-mini

**Which Bernard personality did you use (from Exercise 1)?**
>Version 2. 
Both models were run until 10:00. The primary analysis used the same 08:00–08:30 window for both models. An extended window was used as a supplementary analysis if either run contained no conversations involving Bernard.

### 2.2 Qualitative comparison

**Do the agents sound different across models? Describe the differences in tone, vocabulary, and interaction style. Provide at least one conversation excerpt from each model.**

Model A excerpt:

>

Model B excerpt:

>

Your analysis:

### 2.3 Valence comparison

(Attach or paste your valence trajectory plot)

**Which model produces more emotional variance?**

Your answer:

### 2.4 JSON validation failures

| | Model A | Model B |
|---|---|---|
| Total LLM calls | | |
| Failed validations | | |
| Failure rate | | |

**What does this tell you about using different models in agent simulations?**

Your answer:


### 2.5 Reflection

**The architecture and personality descriptions are identical. What does it mean that behaviour differs anyway?**

Your answer:


---

## Exercise 3: Enabling the Negativity Bias

The negativity bias consists of two mechanisms:

   - **Valence-weighted retrieval:** The standard architecture retrieves memories based on recency, relevance, and importance only (the valence weight is set to zero). To enable valence-aware retrieval, the agent needs a non-zero valence weight. The negativity bias multiplier controls how much more strongly negative memories are favoured over positive ones during retrieval — a value of 1.5 means negative memories are retrieved 1.5× more readily.

   - **Asymmetric sensory encoding:** When enabled, negatively valenced events (≤ −3 on a −10 to +10 scale) are stored with expanded perceptual detail (richer descriptions of what the agent expereinced). When disabled, all events are stored with the same level of detail regardless of valence.

   Look at Dolores's `scratch.json` file. Find the fields that control these mechanisms and set them appropriately. Maeve's scratch file should remain unchanged — she is your control.

**Which Bernard personality did you use (from Exercise 1, the one you used in Exercise 2)? Paste his `innate` and `learned` fields.**

Your answer:

### 3.1 Valence trajectories

(Attach or paste your plot of Dolores vs Maeve valence over time)

### 3.2 Descriptive statistics

| Agent | Overall valence | Thought valence |
|---|---|---|
| Dolores (neg. bias) | | |
| Maeve (control) | | |

**Cohen's d:**

**Interpretation (small / medium / large effect):**

### 3.3 Thought description comparison

**Dolores example thought (negative memory):**

>

**Maeve example thought (comparable event):**

>

**Is Dolores's description longer and more sensorially detailed?**

Your answer:

### 3.4 Memory intrusion check

If your simulation included off-duty hours, answer the following. If not, write "Simulation was too short to observe off-duty reflections."

**Did you find work-related content in Dolores's evening reflections? Paste any examples:**

>

**Did you find work-related content in Maeve's evening reflections? Paste any examples:**

>

**Is there a difference between the two agents?**

Your answer:

### 3.5 Consistency across runs (if applicable)

| Run | Dolores valence | Maeve valence | Cohen's d |
|---|---|---|---|
| Run 1 | | | |
| Run 2 | | | |
| Run 3 | | | |

### 3.6 Tracing the mechanism

**You enabled two changes: negative memories get higher retrieval scores, and negative events get stored with more detail. Looking at your logs, can you trace how these two changes could lead to the valence decline you observed? Think about what happens when a negatively-toned reflection gets stored as a new memory.**

Your answer:

---

## Exercise 4: Daily Plan Quality

### 4.1 Original plan problems

**Paste an example of a problematic daily plan and annotate what is wrong with it:**

>

### 4.2 Your planning rules

List the rules you wrote:

1.
2.
3.
4.
5.

### 4.3 Improved plan

**Paste an example of a daily plan generated with your rules:**

>

### 4.4 Downstream effects

**Do agents with better plans behave differently? More social interactions? Different valence patterns?**

Your answer:

---

## General Reflection

**What was the most surprising finding across all exercises?**

Your answer:

**If you were designing an agent simulation for a real application, what would you do differently based on what you learned?**

Your answer:
