"""Extract exercise 2 evidence, statistics and valence plots."""

import argparse
import csv
from collections import Counter
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TIME_FORMAT = "%B %d, %Y, %H:%M:%S"
VALENCE_COLUMNS = [
    "model", "persona", "node_id", "type", "time", "valence",
    "description", "source",
]
ACTIVITY_COLUMNS = ["model", "time", "persona", "location", "description", "source"]
FAILURE_COLUMNS = [
    "model", "run_id", "llm_id", "prompt_name", "sim_time", "step",
    "msg", "reason", "attempt", "error", "source", "line",
]
TABLE_NAMES = [
    "valence", "valence_summary", "validation_summary", "validation_failures",
    "conversation_summary", "activity_changes", "valence_combined_summary",
]
CONTROL_FIELDS = [
    "innate", "learned", "lifestyle", "daily_plan_req", "recency_w",
    "relevance_w", "importance_w", "valence_w", "asymetric_encoding",
    "negativity_bias",
]


def get_args():
    # take the output directory, observation window and models from the command line
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="directory for the generated files")
    parser.add_argument("--start", default="2023-02-13T08:00:00", help="window start in game time, inclusive")
    parser.add_argument("--end", default="2023-02-13T08:30:00", help="window end in game time, exclusive")
    parser.add_argument("--models", nargs="+", default=["gpt-5.4-mini", "qwen3:4b-instruct-16k"],
                        help="model IDs matching ex2_<model> folders, default: %(default)s")
    parser.add_argument("--smooth", type=int, default=0,
                        help="0 connects means at exact timestamps; positive values use minute bins, default: %(default)s")
    parser.add_argument("--memory-types", nargs="+", choices=["event", "thought", "chat"],
                        default=["event", "thought"],
                        help="memory types to analyze; selecting all three also exports combined results")
    parser.add_argument("--simulation-dir", type=Path, default=ROOT / "simulation")
    parser.add_argument("--movement-dir", type=Path, default=ROOT,
                        help="folder containing ex2_<model>/_state/movement")
    parser.add_argument("--log-dir", type=Path, default=ROOT / "logs")
    args = parser.parse_args()
    try:
        time_check(args.start, args.end)
    except ValueError as error:
        parser.error(str(error))
    if args.smooth < 0:
        parser.error("--smooth must be non-negative")
    if len(set(args.models)) != len(args.models):
        parser.error("--models must not contain duplicates")
    if len(set(args.memory_types)) != len(args.memory_types):
        parser.error("--memory-types must not contain duplicates")
    for model in args.models:
        if Path(model).name != model or model in {".", ".."}:
            parser.error("model IDs must be folder names, not paths")
    return args


def game_time(value):
    # game timestamps without an explicit timezone are interpreted as utc
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        parsed = datetime.strptime(value, TIME_FORMAT)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def time_check(start, end):
    start, end = game_time(start), game_time(end)
    if start >= end:
        raise ValueError("--start must be earlier than --end")
    return start, end


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_path(path):
    # keep source paths readable inside the repository
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def get_map(maze):
    # use actual coordinates to locate agents because activity addresses are destinations
    width = read_json(maze / "maze_meta_info.json")["maze_width"]
    with (maze / "special_blocks" / "sector_blocks.csv").open() as file:
        sectors = {row[0].strip(): row[-1].strip() for row in csv.reader(file)}
    with (maze / "maze" / "sector_maze.csv").open() as file:
        sector_grid = [value.strip() for value in next(csv.reader(file))]
    return width, sectors, sector_grid


def collect_persona_settings(simulation, meta):
    personas, memories = {}, {}
    for person in meta["persona_names"]:
        folder = simulation / "personas" / person / "bootstrap_memory"
        personas[person] = read_json(folder / "scratch.json")
        memories[person] = read_json(folder / "associative_memory" / "nodes.json")
    return personas, memories


def collect_valence(memories, model_label, start, end, simulation, memory_types):
    records = []
    for persona, nodes in memories.items():
        source = simulation / "personas" / persona / "bootstrap_memory" / "associative_memory" / "nodes.json"
        for node_id, node in nodes.items():
            if node["type"] not in memory_types or node.get("valence") is None:
                continue
            created = game_time(node["created"])
            if not start <= created < end:
                continue
            records.append({
                "model": model_label, "persona": persona, "node_id": node_id,
                "type": node["type"], "time": created, "valence": node["valence"],
                "description": node.get("description", ""), "source": source_path(source),
            })
    frame = pd.DataFrame(records, columns=VALENCE_COLUMNS)
    frame["time"] = pd.to_datetime(frame["time"], utc=True)
    frame["valence"] = pd.to_numeric(frame["valence"])
    return frame.sort_values(["persona", "type", "time", "node_id"])


def summarize_valence(valence, models, personas, memory_types):
    # keep empty groups visible instead of treating missing memories as neutral scores
    index = pd.MultiIndex.from_product(
        [models, personas, memory_types], names=["model", "persona", "type"]
    )
    if valence.empty:
        summary = pd.DataFrame(index=index, columns=["n", "mean", "variance", "std", "minimum", "maximum"], dtype=float)
    else:
        summary = valence.groupby(["model", "persona", "type"])["valence"].agg(
            n="count", mean="mean", variance="var", std="std", minimum="min", maximum="max"
        ).reindex(index)
    summary["n"] = summary["n"].fillna(0).astype(int)
    return summary.reset_index()


def combine_valence(valence, models, personas):
    # pool raw nodes instead of averaging the three type means
    combined = valence.assign(type="combined")
    summary = summarize_valence(combined, models, personas, ["combined"])
    for kind in ["event", "thought", "chat"]:
        counts = valence[valence["type"] == kind].groupby(["model", "persona"]).size()
        summary[f"n_{kind}"] = [int(counts.get((model, persona), 0))
                                for model, persona in zip(summary["model"], summary["persona"])]
    return combined, summary


def collect_plot_data(valence, start, end, smooth=0):
    columns = ["model", "persona", "type", "time", "mean", "n"]
    groups = []
    for (model, persona, kind), group in valence.groupby(["model", "persona", "type"]):
        scores = group.set_index("time")["valence"].sort_index()
        if smooth:
            bins = pd.date_range(start, end, freq=f"{smooth}min", inclusive="left")
            values = scores.resample(f"{smooth}min", origin=start).agg(["mean", "count"]).reindex(bins)
        else:
            # average simultaneous memories and connect only actual observation times
            values = scores.groupby(level=0, sort=True).agg(["mean", "count"])
        values = values.rename(columns={"count": "n"})
        values["n"] = values["n"].fillna(0).astype(int)
        values.index.name = "time"
        groups.append(values.reset_index().assign(model=model, persona=persona, type=kind))
    return pd.concat(groups, ignore_index=True)[columns] if groups else pd.DataFrame(columns=columns)


def plot_filename(kind, smooth=0):
    stem = "combined" if kind == "combined" else f"{kind}s"
    suffix = f"_{smooth}min" if smooth else ""
    return f"valence_{stem}{suffix}.png"


def draw_valence(valence, plot_data, output, models, personas, start, end, memory_types, smooth):
    colors = dict(zip(models, plt.get_cmap("tab10").colors * (len(models) // 10 + 1)))
    for kind in memory_types:
        fig, axes = plt.subplots(len(personas), 1, figsize=(8, 2.2 * len(personas)),
                                 sharex=True, squeeze=False)
        for ax, persona in zip(axes[:, 0], personas):
            subset = valence[(valence["persona"] == persona) & (valence["type"] == kind)]
            for model in models:
                raw = subset[subset["model"] == model]
                ax.scatter(raw["time"], raw["valence"], s=18, alpha=0.4, color=colors[model])
                line = plot_data[(plot_data["model"] == model)
                                 & (plot_data["persona"] == persona)
                                 & (plot_data["type"] == kind)].sort_values("time")
                ax.plot(line["time"], line["mean"], marker="o", markersize=3,
                        linewidth=1.1, color=colors[model])
            if subset.empty:
                ax.text(0.5, 0.5, "No memories in this window", ha="center", transform=ax.transAxes)
            ax.set_title(persona, loc="left", fontsize=11)
            ax.set_ylabel("Valence")
            ax.set_ylim(-10.5, 10.5)
            ax.set_yticks([-10, -5, 0, 5, 10])
            ax.set_xlim(start, end)
            ax.axhline(0, color="0.7", linewidth=0.7)
            ax.grid(alpha=0.2)
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=timezone.utc))
        handles = [Line2D([], [], color=colors[model], marker="o", label=model) for model in models]
        label = "Combined memory" if kind == "combined" else kind.capitalize()
        fig.suptitle(f"{label} valence by model | {start:%Y-%m-%d %H:%M}–{end:%H:%M} UTC",
                     fontsize=12, y=0.99)
        fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.96),
                   ncol=min(len(models), 3), frameon=False)
        axes[-1, 0].set_xlabel("Game time (UTC)")
        fig.tight_layout(rect=[0, 0, 1, 0.90])
        fig.savefig(output / plot_filename(kind, smooth), dpi=180)
        plt.close(fig)


def collect_logs(folder, warnings):
    # combine only the jsonl logs from this model's experiment folder
    records = []
    for path in sorted(folder.glob("*/run.jsonl")):
        current_time, current_step = None, None
        with path.open(encoding="utf-8") as file:
            for number, line in enumerate(file, 1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    if not line.endswith("\n"):
                        warnings.append(f"Ignored an incomplete final log record: {source_path(path)}:{number}")
                        continue
                    raise ValueError(f"Invalid JSONL record: {source_path(path)}:{number}")
                if record.get("msg") == "step_start":
                    current_time, current_step = record["sim_time"], record["step"]
                record.update(_source=source_path(path), _line=number,
                              _sim_time=record.get("sim_time", current_time),
                              _step=record.get("step", current_step))
                records.append(record)
    if not records:
        warnings.append(f"No JSONL logs found in {source_path(folder)}")
    return records


def call_key(row):
    return row.get("run_id", row.get("_source", "")), row["llm_id"]


def failure_rate(failures, total):
    # leave undefined rates blank rather than treating an empty window as zero failures
    return failures / total if total else None


def validation_summary(logs):
    # count each returned response once; final failures may repeat the last response
    starts, successes, failures, api_errors = set(), set(), set(), set()
    responses = {}
    for row in logs:
        if not row.get("llm_id"):
            continue
        key, message = call_key(row), row.get("msg")
        if message == "llm_call_start":
            starts.add(key)
        elif message in {"llm_retry", "llm_call_ok"}:
            attempt = row.get("attempt") if message == "llm_retry" else row.get("attempts_total", 1)
            responses[(key, attempt)] = row.get("reason", "unknown") if message == "llm_retry" else "ok"
            if message == "llm_call_ok":
                successes.add(key)
        elif message == "llm_call_fail":
            failures.add(key)
            if "attempt" in row and "output_raw" not in row:
                api_errors.add(key)
    reasons = Counter(responses.values())
    count = len(responses)
    json_failures = reasons["json_unmarshal"] + reasons["json_validation"]
    business_failures = reasons["validation"]
    unknown_failures = sum(n for reason, n in reasons.items()
                           if reason not in {"ok", "json_unmarshal", "json_validation", "validation"})
    validation_failures = json_failures + business_failures
    response_failures = validation_failures + unknown_failures
    complete = successes | failures
    # count each started logical call once even if several responses fail validation
    json_calls = {key for (key, attempt), reason in responses.items()
                  if reason in {"json_unmarshal", "json_validation"}}
    validation_calls = {key for (key, attempt), reason in responses.items()
                        if reason in {"json_unmarshal", "json_validation", "validation"}}
    logical_json_failures = len(starts & json_calls)
    logical_validation_failures = len(starts & validation_calls)
    return {
        "logical_calls_started": len(starts), "logical_calls_completed": len(complete),
        "successful_logical_calls": len(successes), "incomplete_calls": len(starts - complete),
        "response_attempts": count,
        "successful_responses": reasons["ok"],
        "json_parse_failures": reasons["json_unmarshal"], "schema_failures": reasons["json_validation"],
        "json_failures": json_failures, "business_rule_failures": business_failures,
        "validation_failures": validation_failures, "unknown_retry_failures": unknown_failures,
        "response_failures": response_failures,
        "logical_calls_with_json_failures": logical_json_failures,
        "logical_calls_with_validation_failures": logical_validation_failures,
        "final_call_failures": len(failures), "api_error_calls": len(api_errors),
        # response-level rates use returned responses, including retries
        "json_failure_rate": failure_rate(json_failures, count),
        "business_failure_rate": failure_rate(business_failures, count),
        "validation_failure_rate": failure_rate(validation_failures, count),
        "unknown_retry_failure_rate": failure_rate(unknown_failures, count),
        "response_failure_rate": failure_rate(response_failures, count),
        # incidence uses started calls; terminal outcomes use completed calls
        "logical_json_failure_rate": failure_rate(logical_json_failures, len(starts)),
        "logical_validation_failure_rate": failure_rate(logical_validation_failures, len(starts)),
        "final_call_failure_rate": failure_rate(len(failures), len(complete)),
        "api_error_rate": failure_rate(len(api_errors), len(complete)),
    }


def collect_validation(logs, model, start, end):
    # restrict both counts and error details to the selected window
    window_logs = [row for row in logs if row.get("_sim_time")
                   and start <= game_time(row["_sim_time"]) < end]
    totals = {"model": model, "window_start": start.isoformat(), "window_end": end.isoformat(),
              **validation_summary(window_logs)}
    details = []
    for row in window_logs:
        if row.get("msg") not in {"llm_retry", "llm_call_fail", "llm_json_validation_error"}:
            continue
        error = row.get("err") or json.dumps(row.get("validation_errors", []), ensure_ascii=False)
        details.append({
            "model": model, "run_id": row.get("run_id"), "llm_id": row.get("llm_id"),
            "prompt_name": row.get("prompt_name"), "sim_time": row.get("_sim_time"),
            "step": row.get("_step"), "msg": row["msg"], "reason": row.get("reason", ""),
            "attempt": row.get("attempt", row.get("attempts_total")), "error": error,
            "source": row["_source"], "line": row["_line"],
        })
    return totals, details


def collect_movements(folder, model, maze, start, end):
    width, sectors, sector_grid = maze
    conversations, activities, first_cafe, locations = [], [], {}, {}
    previous_chats, previous_activities = set(), {}
    first_time = last_time = None
    paths = sorted(folder.glob("*.json"), key=lambda path: int(path.stem))
    for path in paths:
        movement = read_json(path)
        current_time = game_time(movement["meta"]["curr_time"])
        first_time = first_time or current_time
        last_time = current_time
        current_chats = set()
        for person, state in movement["persona"].items():
            # get person's location
            x, y = state["movement"]
            index = y * width + x
            location = sectors.get(sector_grid[index], "outside") if 0 <= x < width and 0 <= index < len(sector_grid) else "outside"
            locations[person] = location
            if location == "Hobbs Cafe" and person not in first_cafe:
                first_cafe[person] = current_time
            description = state["description"]
            # record all activity changes
            if description != previous_activities.get(person):
                if start <= current_time < end:
                    activities.append({"model": model, "time": current_time, "persona": person,
                                       "location": location, "description": description,
                                       "source": source_path(path)})
                previous_activities[person] = description
            # record chat, and only count once copy of each conversation
            chat = state.get("chat")
            if chat:
                signature = tuple(tuple(turn) for turn in chat)
                # count both speakers' copies once, but retain later separate conversations
                if (start <= current_time < end and signature not in previous_chats
                        and signature not in current_chats):
                    conversations.append({
                        "time": current_time, "speakers": sorted({speaker for speaker, text in chat}),
                        "chat": chat, "source": source_path(path),
                    })
                current_chats.add(signature)
        previous_chats = current_chats
    return {"window_chats": conversations, "activities": activities,
            "first_time": first_time, "last_time": last_time,
            "first_cafe": first_cafe, "locations": locations}


def collect_turns(model, conversations):
    # keep turns in memory for conversation summary statistics
    turns = []
    for number, conversation in enumerate(conversations, 1):
        for turn, (speaker, text) in enumerate(conversation["chat"], 1):
            turns.append({"model": model, "conversation": number, "time": conversation["time"],
                          "persona": speaker, "turn": turn, "text": text, "source": conversation["source"]})
    return turns


def write_conversations(output, model, conversations, start, end):
    # keep complete dialogue and source paths in the same readable style as exercise 1
    bernard_chats = sum("Bernard Lowe" in chat["speakers"] for chat in conversations)
    report = [
        f"Exercise 2 — {model}", "",
        "SELECTED WINDOW — conversation start times, inclusive start and exclusive end",
        f"Window: [{start.isoformat()}, {end.isoformat()})",
        f"Conversations: {len(conversations)}; involving Bernard: {bernard_chats}", "",
        "CONVERSATIONS — starting in the selected window, complete transcripts",
    ]
    for number, conversation in enumerate(conversations, 1):
        report.extend([
            f"\nConversation {number} | {conversation['time'].isoformat()}",
            f"Participants: {', '.join(conversation['speakers'])}",
            f"Source: {conversation['source']}",
            *[f"{speaker}: {text}" for speaker, text in conversation["chat"]],
        ])
    if not conversations:
        report.append("\nNo conversations started in this window.")
    (output / f"conversation_{model}.txt").write_text("\n".join(report) + "\n", encoding="utf-8")


def conversation_summary(turns, models, personas):
    summaries = []
    for model in models:
        for persona in personas:
            selected = [turn for turn in turns if turn["model"] == model and turn["persona"] == persona]
            texts = [" ".join(turn["text"].lower().split()) for turn in selected]
            summaries.append({
                "model": model, "persona": persona,
                "conversations": len({turn["conversation"] for turn in selected}),
                "turns": len(selected),
                "mean_words_per_turn": sum(len(turn["text"].split()) for turn in selected) / len(selected) if selected else None,
                "repeated_turn_fraction": (len(texts) - len(set(texts))) / len(texts) if texts else None,
            })
    return summaries


def write_plans(output, name, model, personas, movements, saved_time, simulation):
    # retain daily plans separately and label the actual snapshot time
    report = [f"Exercise 2 — {model}", "Daily plans and final saved state",
              f"Saved clock: {saved_time.isoformat()}",
              "These are full-day plans from the saved snapshot, not the state at the analysis window end.", ""]
    for person, scratch in personas.items():
        source = simulation / "personas" / person / "bootstrap_memory" / "scratch.json"
        arrival = movements["first_cafe"].get(person)
        report.extend([
            person, f"Source: {source_path(source)}",
            f"First physical arrival at Hobbs Cafe: {arrival.isoformat() if arrival else 'not observed'}",
            f"Final physical location: {movements['locations'].get(person, 'not observed')}",
            f"Final activity: {scratch.get('act_description')}", "High-level daily plan:",
            *[f"  - {activity}" for activity in scratch.get("daily_req", [])],
            "Original hourly schedule:",
        ])
        minute = 0
        for activity, duration in scratch.get("f_daily_schedule_hourly_org", []):
            end = minute + duration
            report.append(f"  {minute//60:02}:{minute%60:02}–{end//60:02}:{end%60:02} {activity}")
            minute = end
        report.append("")
    (output / f"plans_{name}.txt").write_text("\n".join(report) + "\n", encoding="utf-8")


def clean_old_outputs(output, models, memory_types, smooth=0):
    # remove only known generated files that are no longer part of this analysis
    obsolete = ["run_summary.csv", "valence_plot_data.csv", "validation_by_prompt.csv",
                "persona_settings.json", "analysis_notes.txt"]
    for model in models:
        obsolete.append(f"conversations_ex2_{model}.txt")
    if all((output / f"conversation_{model}.txt").is_file() for model in models):
        obsolete.extend(["conversation_turns.csv", "conversation_turns.tsv"])
    selected = set(memory_types)
    if selected == {"event", "thought", "chat"}:
        selected.add("combined")
    else:
        obsolete.extend(["valence_combined_summary.csv", "valence_combined_summary.tsv"])
    for kind in ["event", "thought", "chat", "combined"]:
        stem = "combined" if kind == "combined" else f"{kind}s"
        candidates = [output / plot_filename(kind), *output.glob(f"valence_{stem}_*min.png")]
        for path in candidates:
            if kind not in selected or path.name != plot_filename(kind, smooth):
                obsolete.append(path.name)
    obsolete.append("valence_combined{f_smooth}.png")
    # remove old csv exports only after the corresponding tsv exists
    for name in TABLE_NAMES:
        if (output / f"{name}.tsv").is_file():
            obsolete.append(f"{name}.csv")
    for filename in obsolete:
        (output / filename).unlink(missing_ok=True)


def write_tsv(path, rows, columns=None):
    # quote fields when needed to preserve tabs, line breaks and quotation marks
    frame = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows, columns=columns)
    frame.to_csv(path, sep="\t", index=False, encoding="utf-8", quoting=csv.QUOTE_MINIMAL)


def main():
    args = get_args()
    start, end = time_check(args.start, args.end)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    maze = get_map(ROOT / "maze" / "the_spiral" / "matrix")
    warnings, frames, turns, validation_totals, failures, activities = [], [], [], [], [], []
    settings, all_personas = {}, set()

    for model in args.models:
        name = f"ex2_{model}"
        simulation = args.simulation_dir.resolve() / name
        meta = read_json(simulation / "reverie" / "meta.json")
        # collect persona settings and memories
        personas, memories = collect_persona_settings(simulation, meta)
        all_personas.update(personas)
        settings[model] = {person: {key: scratch.get(key) for key in CONTROL_FIELDS}
                           for person, scratch in personas.items()}
        frames.append(collect_valence(memories, model, start, end, simulation, args.memory_types))
        logs = collect_logs(args.log_dir.resolve() / name, warnings)
        # collect validation results within the window
        totals, details = collect_validation(logs, model, start, end)
        validation_totals.append(totals)
        failures.extend(details)
        # collect movements and conversations
        movements = collect_movements(args.movement_dir.resolve() / name / "_state" / "movement",
                                      model, maze, start, end)
        activities.extend(movements["activities"])
        selected = movements["window_chats"]
        write_conversations(output, model, selected, start, end)
        turns.extend(collect_turns(model, selected))
        # keep coverage checks without exporting a separate run summary
        saved_time = game_time(meta["curr_time"])
        write_plans(output, name, model, personas, movements, saved_time, simulation)
        last_movement = movements["last_time"]
        movement_end = last_movement + timedelta(seconds=meta["sec_per_step"]) if last_movement else None
        coverage = movement_end is not None and movements["first_time"] <= start and saved_time >= end and movement_end >= end
        if not coverage:
            warnings.append(f"{model}: saved state and movements do not both cover the complete selected window.")
        bernard_chats = sum("Bernard Lowe" in chat["speakers"] for chat in selected)
        if not bernard_chats:
            warnings.append(f"{model}: no conversation involving Bernard starts in the selected window.")
        print(f"{model}: {len(selected)} conversations; Bernard: {bernard_chats}; valence nodes: {len(frames[-1])}")

    # compare saved control settings without exporting another settings file
    baseline = args.models[0]
    for model in args.models[1:]:
        if settings[model] != settings[baseline]:
            warnings.append(f"Saved persona settings differ between {baseline} and {model}; check their scratch.json files.")

    # export only the selected window's evidence and summaries
    personas = sorted(all_personas)
    window = {"window_start": start.isoformat(), "window_end": end.isoformat()}
    valence = pd.concat(frames, ignore_index=True)
    stats = summarize_valence(valence, args.models, personas, args.memory_types)
    plot_data = collect_plot_data(valence, start, end, args.smooth)
    write_tsv(output / "valence.tsv", valence)
    write_tsv(output / "valence_summary.tsv", stats.assign(**window))
    write_tsv(output / "validation_summary.tsv", validation_totals)
    write_tsv(output / "validation_failures.tsv", failures, FAILURE_COLUMNS)
    conversation_stats = pd.DataFrame(conversation_summary(turns, args.models, personas))
    write_tsv(output / "conversation_summary.tsv", conversation_stats.assign(**window))
    write_tsv(output / "activity_changes.tsv", activities, ACTIVITY_COLUMNS)
    draw_valence(valence, plot_data, output, args.models, personas, start, end,
                 args.memory_types, args.smooth)

    # add pooled statistics and a plot only when all three types are selected
    if set(args.memory_types) == {"event", "thought", "chat"}:
        combined, combined_stats = combine_valence(valence, args.models, personas)
        combined_plot = collect_plot_data(combined, start, end, args.smooth)
        write_tsv(output / "valence_combined_summary.tsv", combined_stats.assign(**window))
        draw_valence(combined, combined_plot, output, args.models, personas, start, end,
                     ["combined"], args.smooth)

    clean_old_outputs(output, args.models, args.memory_types, args.smooth)
    for warning in warnings:
        print(f"Warning: {warning}")
    print(f"Results saved to {output}")


if __name__ == "__main__":
    main()
