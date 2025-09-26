# Child LLM – Consciousness Data Generation

This project explores consciousness, awareness and attention, world-modeling, and interoception as a substrate-independent phenomenon. Current large language models are trained on a robust corpus of information, allowing for intelligent output but lacking internal modeling capabilities. While these models may be capable of articulating a conscious experience, this likely stems from comprehensive human documentation of the conscious experience in the training dataset. The ‘Child LLM’ project addresses this problem by curating the training dataset to reflect an inner monologue. Specifically, this inner monologue will document the first five years of life, in which an agent becomes aware of internal signaling, develops perception of external stimuli, and builds world models. This framework views the inner monologue as an information processing phenomenon that can be explained computationally, independent of a specific biological substrate. 

## Project structure

```
data_generation/
├── child_llm/
│   ├── generators/
│   ├── models/
│   └── pipeline/
├── chunked_iterative_generator.py
├── chunked_two_pass_generator.py
├── simple_validation.py
├── single_pass_generator.py
├── my_monologue/
│   ├── scenarios/
│   ├── timeline/
│   └── vocabulary/
├── requirements.txt
└── README.md
```

## Setup

```bash
pip install -r requirements.txt
```

Set your API key in the environment before running scripts:

```bash
export OPENAI_API_KEY="..."
```

## Usage

Single‑pass generation for a given date:

```bash
python single_pass_generator.py --date 2025-01-01 \
  --scenario my_monologue/scenarios/my_child.json \
  --timeline my_monologue/timeline/master_timeline.json
```

Chunked generation (two‑pass):

```bash
python chunked_two_pass_generator.py --date 2025-01-01 \
  --scenario my_monologue/scenarios/my_child.json \
  --timeline my_monologue/timeline/master_timeline.json
```

Iterative chunked generation (debug/development):

```bash
python chunked_iterative_generator.py day 2025-01-01
```

Validate an output file:

```bash
python simple_validation.py path/to/generated/day.json
```

## Data and configuration

- Scenarios live in `my_monologue/scenarios/`.
- The long‑horizon timeline is in `my_monologue/timeline/master_timeline.json`.
- Age‑appropriate vocabulary bands are in `my_monologue/vocabulary/`.
