"""extract exercise 1 evidence: python3 scripts/analyze_ex1.py <output directory>"""

import argparse
import csv
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path

# take the output directory, observation window and versions from the command line
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, required=True, help="directory for the generated files")
parser.add_argument("--start", default="2023-02-13T08:00:00", help="window start in game time, inclusive")
parser.add_argument("--end", default="2023-02-13T08:30:00", help="window end in game time, exclusive")
parser.add_argument("--versions", nargs="+", type=int, choices=[1, 2, 3], default=[1, 2, 3], help="experiment versions to analyze, default: 1 2 3")
args = parser.parse_args()

OUTPUT = args.output
OUTPUT.mkdir(parents=True, exist_ok=True)

# experiment versions and their prompting styles
VERSIONS = args.versions
STYLES = {1: "adjectives", 2: "full sentences", 3: "concrete examples"}
ROOT = Path(__file__).resolve().parents[1]
TIME_FORMAT = "%B %d, %Y, %H:%M:%S"
# game timestamps without an explicit timezone are interpreted as utc
WINDOW_START = datetime.fromisoformat(args.start.replace("Z", "+00:00"))
WINDOW_END = datetime.fromisoformat(args.end.replace("Z", "+00:00"))
if WINDOW_START.tzinfo is None:
    WINDOW_START = WINDOW_START.replace(tzinfo=timezone.utc)
if WINDOW_END.tzinfo is None:
    WINDOW_END = WINDOW_END.replace(tzinfo=timezone.utc)
if WINDOW_START >= WINDOW_END:
    parser.error("--start must be earlier than --end")

# use actual coordinates to locate agents because activity addresses are destinations
maze = ROOT / "maze" / "the_spiral" / "matrix"
width = json.loads((maze / "maze_meta_info.json").read_text())["maze_width"]
with (maze / "special_blocks" / "sector_blocks.csv").open() as file:
    sectors = {row[0].strip(): row[-1].strip() for row in csv.reader(file)}
with (maze / "maze" / "sector_maze.csv").open() as file:
    sector_grid = [value.strip() for value in next(csv.reader(file))]

summaries = []
for version in VERSIONS:
    name = f"ex1_bernard_v{version}"
    simulation = ROOT / "simulation" / name
    meta = json.loads((simulation / "reverie" / "meta.json").read_text())
    # read each agent's persona settings and saved memories
    personas = {}
    memories = {}
    for person in meta["persona_names"]:
        folder = simulation / "personas" / person / "bootstrap_memory"
        personas[person] = json.loads((folder / "scratch.json").read_text())
        memories[person] = json.loads(
            (folder / "associative_memory" / "nodes.json").read_text()
        )

    # combine logs from repeated starts of the same experiment
    logs = []
    for path in sorted((ROOT / "logs" / name).glob("*/run.jsonl")):
        logs.extend(json.loads(line) for line in path.read_text().splitlines())
    events = Counter(row["msg"] for row in logs)
    step_times = [row["sim_time"] for row in logs if row["msg"] == "step_start"]

    # count each conversation once while active, including both speakers' copies
    # count a later identical conversation again if the earlier one has ended
    conversations = []
    previous_chats = set()
    previous_activities = {}
    timeline = []
    first_cafe = {}
    # sort step numbers numerically so step 10 follows step 9 rather than step 1
    movement_files = sorted(
        (ROOT / name / "_state" / "movement").glob("*.json"),
        key=lambda path: int(path.stem),
    )
    for path in movement_files:
        movement = json.loads(path.read_text())
        current_time = datetime.strptime(
            movement["meta"]["curr_time"], TIME_FORMAT
        ).replace(tzinfo=timezone.utc)
        current_chats = set()
        locations = {}
        for person, state in movement["persona"].items():
            x, y = state["movement"]
            location = sectors.get(sector_grid[y * width + x], "outside")
            locations[person] = location
            if location == "Hobbs Cafe" and person not in first_cafe:
                first_cafe[person] = current_time.strftime("%H:%M:%S")
            description = state["description"]
            # retain activity changes instead of repeating every simulation step
            if description != previous_activities.get(person):
                timeline.append(
                    f"{current_time:%H:%M:%S} | {person} | actual location: "
                    f"{location} | {description}"
                )
                previous_activities[person] = description

            chat = state["chat"]
            if chat:
                signature = tuple(tuple(turn) for turn in chat)
                if signature not in previous_chats and signature not in current_chats:
                    conversations.append({
                        "time": current_time,
                        "speakers": sorted({speaker for speaker, text in chat}),
                        "chat": chat,
                        "source": str(path.relative_to(ROOT)),
                    })
                current_chats.add(signature)
        previous_chats = current_chats

    # require bernard to be a speaker rather than merely mentioned in the dialogue
    bernard_chats = [c for c in conversations if "Bernard Lowe" in c["speakers"]]
    # select conversations by start time within the requested observation window
    window_chats = [c for c in conversations
                    if WINDOW_START <= c["time"] < WINDOW_END]
    window_bernard_chats = [c for c in window_chats if "Bernard Lowe" in c["speakers"]]
    bernard = personas["Bernard Lowe"]
    summaries.append({
        "version": version,
        "prompting_style": STYLES[version],
        "first_logged_sim_time": step_times[0],
        "last_logged_step_start": step_times[-1],
        "last_saved_movement": current_time.isoformat(),
        "all_conversations": len(conversations),
        "bernard_conversations": len(bernard_chats),
        "window_start": WINDOW_START.isoformat(),
        "window_end": WINDOW_END.isoformat(),
        "data_reaches_window_end": current_time >= WINDOW_END,
        "conversations_in_window": len(window_chats),
        "bernard_conversations_in_window": len(window_bernard_chats),
        "llm_calls_started": events["llm_call_start"],
        "llm_retry_records": events["llm_retry"],
        "llm_call_fail_records": events["llm_call_fail"],
    })

    # collect persona prompts and run statistics for the exercise 1 report
    report = [
        f"Exercise 1 — Version {version}",
        f"Prompting style: {STYLES[version]}",
        f"Bernard innate: {bernard['innate']!r}",
        f"Bernard learned: {bernard['learned']!r}",
        "",
        "RUN SUMMARY — full run",
        f"First logged game time: {step_times[0]}",
        f"Last logged step start: {step_times[-1]}",
        f"Saved clock (next step): {meta['curr_time']}",
        f"Last saved movement: {current_time.isoformat()}",
        f"All conversations: {len(conversations)}; involving Bernard: {len(bernard_chats)}",
        f"LLM calls started: {events['llm_call_start']}; retry records: "
        f"{events['llm_retry']}; final failure records: {events['llm_call_fail']}",
        "Retries and final failures are separate records, not a single failure rate.",
        "",
        "SELECTED WINDOW — conversation start times, inclusive start and exclusive end",
        f"Window: [{WINDOW_START.isoformat()}, {WINDOW_END.isoformat()})",
        f"Saved data reaches window end: {current_time >= WINDOW_END}",
        f"Conversations: {len(window_chats)}; involving Bernard: {len(window_bernard_chats)}",
        "",
        "PLANS AND FINAL STATE — full run",
    ]
    for person, scratch in personas.items():
        counts = Counter(node["type"] for node in memories[person].values())
        report.extend([
            f"\n{person}",
            f"Source: simulation/{name}/personas/{person}/bootstrap_memory/scratch.json",
            f"First physical arrival at Hobbs Cafe: {first_cafe.get(person, 'not observed')}",
            f"Final physical location: {locations[person]}",
            f"Final activity: {scratch['act_description']}",
            f"Activity start: {scratch['act_start_time']}; duration: {scratch['act_duration']} minutes",
            f"Activity destination: {scratch['act_address']}",
            f"Memory nodes: {dict(counts)}",
            "High-level daily plan:",
            *[f"  - {activity}" for activity in scratch["daily_req"]],
            "Original hourly schedule:",
        ])
        # convert activity durations into clock times measured from midnight
        minute = 0
        for activity, duration in scratch["f_daily_schedule_hourly_org"]:
            end = minute + duration
            report.append(f"  {minute//60:02}:{minute%60:02}–{end//60:02}:{end%60:02} {activity}")
            minute = end

    # keep complete dialogue and source paths so excerpts can be selected manually
    report.append("\nCONVERSATIONS — starting in the selected window, complete transcripts")
    for number, conversation in enumerate(window_chats, 1):
        report.extend([
            f"\nConversation {number} | {conversation['time'].isoformat()}",
            f"Participants: {', '.join(conversation['speakers'])}",
            f"Source: {conversation['source']}",
            *[f"{speaker}: {text}" for speaker, text in conversation["chat"]],
        ])
    
    report.extend(["\nACTIVITY CHANGES — full run", *timeline])
    (OUTPUT / f"{name}.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Version {version}: {len(window_chats)} conversations in window; "
          f"Bernard: {len(window_bernard_chats)}; data reaches window end: "
          f"{current_time >= WINDOW_END}")

# write one row per version for comparison
with (OUTPUT / "summary.csv").open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=list(summaries[0]))
    writer.writeheader()
    writer.writerows(summaries)

print(f"Results saved to {OUTPUT}")
