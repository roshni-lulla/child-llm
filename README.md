# Child LLM - Consciousness Monologue Generator

A sophisticated system for generating minute-by-minute consciousness data for children across 5 years of development, based on developmental psychology principles.

## 🎯 Overview

This project generates realistic internal monologues and external reality data for children from birth to 5 years old, capturing the evolution of consciousness, language, and cognitive development. The system uses a two-pass generation approach:

1. **External Reality**: Describes the environment, caregiver actions, and sensory stimuli
2. **Internal Monologue**: Captures the child's consciousness experience at their developmental stage

## 🚀 Features

- **Developmental Accuracy**: Based on Piagetian stages and developmental psychology
- **Two-Pass Generation**: Separates external reality from internal experience
- **Multiple Generation Methods**: Single-pass (recommended) and chunked approaches
- **5-Year Timeline**: Complete developmental progression from birth to age 5
- **Vocabulary Bands**: Age-appropriate language constraints and forbidden patterns
- **Memory System**: Maintains coherence across days, weeks, and months
- **Robust Error Handling**: Graceful fallback for API issues

## 📁 Project Structure

```
data_generation/
├── child_llm/                    # Core library
│   ├── models/                   # Pydantic data models
│   ├── generators/               # Timeline and vocabulary generators
│   └── pipeline/                 # Generation pipeline components
├── examples/                     # Example scripts and usage
│   ├── chunked_iterative_generator.py
│   ├── single_pass_generator.py
│   └── simple_validation.py
├── my_monologue/                 # Configuration and data
│   ├── scenarios/               # Child profiles and scenarios
│   ├── timeline/                # 5-year developmental timeline
│   └── vocabulary/              # Age-appropriate vocabulary bands
├── generate_monologue.py        # Main entry point
├── chunked_two_pass_generator.py # Core generation engine
└── README.md
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/child-llm.git
   cd child-llm/data_generation
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up OpenAI API key**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

## 🎮 Usage

### Quick Start

Generate a single day using the recommended single-pass method:

```bash
python generate_monologue.py --date 2025-01-01 --method single
```

### Advanced Usage

```bash
# Generate with custom scenario and timeline
python generate_monologue.py \
  --scenario my_monologue/scenarios/my_child.json \
  --timeline my_monologue/timeline/master_timeline.json \
  --date 2025-01-01 \
  --method single \
  --output-dir my_monologue/output

# Generate using chunked method (for debugging)
python generate_monologue.py --date 2025-01-01 --method chunked
```

### Example Scripts

```bash
# Single-pass generation (recommended)
python examples/single_pass_generator.py

# Chunked generation with validation
python examples/chunked_iterative_generator.py day 2025-01-01

# Validate generated content
python examples/simple_validation.py my_monologue/output/year_2025/month_01/day_2025-01-01_single.json
```

## 🧠 Generation Methods

### Single-Pass Generation (Recommended)
- **Advantages**: No JSON parsing errors, no rate limiting, better coherence
- **Model**: GPT-4o with 128k context window
- **Output**: Complete 24-hour day in one API call
- **Use case**: Production generation

### Chunked Generation
- **Advantages**: Handles very large contexts, fallback option
- **Model**: GPT-4o with 12-hour chunks
- **Output**: 48 API calls (2 per hour)
- **Use case**: Debugging, very large contexts

## 📊 Data Structure

### External Reality
```json
{
  "hour": 12,
  "external_reality": [
    {
      "minute": 0,
      "environment": "Bright, stimulating playroom",
      "caregiver_actions": "Active engagement and play",
      "objects_present": "Toys, books, soft blocks",
      "sensory_stimuli": "Colorful lights, gentle music",
      "routine_activity": "Active play and interaction",
      "external_events": "Learning and exploration"
    }
  ]
}
```

### Internal Monologue
```json
{
  "hour": 12,
  "entries": [
    {
      "minute": 0,
      "consciousness_components": {
        "sensory_perception": "Rich visual input, bright colors",
        "interoception": "Comfortable, alert bodily state",
        "attention_focus": "Moving toys and caregiver's face",
        "intention_motive": "Exploration and play",
        "social_interaction": "Engaging with caregiver",
        "vocalization": "Excited babbling sounds",
        "motor_behavior": "Reaching and grasping",
        "emotional_expression": "Curious and excited",
        "environmental_learning": "Discovering cause and effect",
        "reflective_awareness": "High awareness of environment"
      },
      "labels": {
        "arousal_level": "high",
        "dominant_emotion": "curious",
        "cognitive_load": "low",
        "social_context": "with_caregivers"
      }
    }
  ]
}
```

## 🔬 Developmental Psychology Integration

### Age-Appropriate Content
- **0-6 months**: Pre-linguistic sounds, basic sensory processing
- **6-12 months**: First words, object permanence, social referencing
- **1-2 years**: Vocabulary explosion, symbolic play, self-awareness
- **2-3 years**: Complex sentences, theory of mind, emotional regulation
- **3-5 years**: Abstract thinking, moral reasoning, peer relationships

### Consciousness Components
1. **Sensory Perception**: Visual, auditory, tactile, olfactory, gustatory
2. **Interoception**: Internal bodily sensations and needs
3. **Attention Focus**: What the child is focusing on
4. **Intention/Motive**: Basic needs and motivations
5. **Social Interaction**: Caregiver and peer interactions
6. **Vocalization**: Communication attempts and sounds
7. **Motor Behavior**: Physical movements and actions
8. **Emotional Expression**: Emotional states and expressions
9. **Environmental Learning**: What the child is learning
10. **Reflective Awareness**: Level of self-awareness

## ⚙️ Configuration

### Scenario Files
Define child profiles in `my_monologue/scenarios/`:
```json
{
  "monologue_id": "my_child",
  "child_profile": {
    "name": "Ari",
    "birthdate": "2025-01-01",
    "sex": "F",
    "personality": {
      "temperament": "easy",
      "activity_level": "moderate",
      "sociability": "high"
    }
  }
}
```

### Timeline Configuration
The 5-year developmental timeline is automatically generated and stored in `my_monologue/timeline/master_timeline.json`.

## 🧪 Validation

The system includes built-in validation to ensure developmental appropriateness:

```bash
python examples/simple_validation.py path/to/generated/day.json
```

Validation checks:
- Age-appropriate vocabulary usage
- Developmental milestone alignment
- Consciousness component realism
- Temporal consistency

## 🚨 Troubleshooting

### Common Issues

1. **API Key Not Set**:
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

2. **JSON Parsing Errors**:
   - Use single-pass method: `--method single`
   - Ensure you're using GPT-4o model

3. **Rate Limiting**:
   - Single-pass method avoids rate limits
   - Chunked method includes exponential backoff

4. **Memory Issues**:
   - Ensure sufficient disk space for output files
   - Generated files can be large (1-2MB per day)

## 📈 Performance

### Generation Speed
- **Single-pass**: ~30 seconds per day
- **Chunked**: ~5-10 minutes per day

### Output Size
- **Per day**: ~1-2MB JSON file
- **Per week**: ~7-14MB
- **Per month**: ~30-60MB

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Based on developmental psychology research (Piaget, Vygotsky, etc.)
- Inspired by consciousness studies and cognitive development
- Built with modern AI/LLM capabilities

## 📞 Support

For questions, issues, or contributions, please open an issue on GitHub.

---

**Note**: This system generates simulated consciousness data for research and educational purposes. It is not intended to replace professional psychological assessment or therapy.