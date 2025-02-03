# ForgeTube Script Generator & Segmentor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The AI-powered script generation module for automated video production, handling both audio narration and visual scene creation through Gemini API integration.

## Features

- **Multimodal Script Generation**: Simultaneous audio/visual script creation
- **Gemini API Integration**: Leverages Google's latest LLMs for content generation
- **Structured JSON Output**: Standardized format for pipeline integration
- **Parameter Validation**: Automatic validation of technical parameters
- **Iterative Refinement**: Feedback-based script improvement system
- **Temporal Synchronization**: Automatic timestamp alignment (5s intervals)
- **Seed Continuity**: Consistent visual element generation through seed control

## Installation

1. Clone repository:
```bash
git clone -b Naman/Script_Generator_and_Segmentor https://github.com/NamanSingh69/ForgeTube.git
cd ForgeTube/Script Generator and Segmentor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Obtain [Gemini API Key](https://ai.google.dev/)
2. Create `.env` file:
```env
GEMINI_API_KEY=your_api_key_here
```

## Usage

### Basic Script Generation
```python
from script_generator import VideoScriptGenerator

generator = VideoScriptGenerator(api_key="your_gemini_key")
script = generator.generate_script(
    topic="Quantum Computing Basics",
    duration=120,  # seconds
    key_points=["Qubits", "Superposition", "Quantum Entanglement"]
)
```

### Script Refinement
```python
refined_script = generator.refine_script(
    existing_script=script,
    feedback="Make visuals more dramatic and increase narration pace"
)
```

### Output Structure
```json
{
    "topic": "Quantum Computing Basics",
    "audio_script": [
        {
            "timestamp": "00:00",
            "text": "Imagine computers that harness quantum physics...",
            "speaker": "narrator_male",
            "speed": 1.05,
            "pitch": 1.1,
            "emotion": "excited"
        }
    ],
    "visual_script": [
        {
            "timestamp": "00:00",
            "prompt": "Futuristic quantum computer with glowing qubits...",
            "negative_prompt": "low detail, blurry, unrealistic lighting",
            "style": "sci-fi",
            "guidance_scale": 8.5,
            "steps": 70,
            "seed": 1234567
        }
    ]
}
```

Configure in code:
```python
self.model = genai.GenerativeModel('gemini-exp-1206')
```

## Validation Checks

Ensures script integrity through:
- Timestamp sequence validation
- Parameter range checks (speed: 0.9-1.1, guidance_scale: 7.0-12.0)
- Speaker/emotion consistency
- Seed value integrity (6-7 digits)
- Aspect ratio enforcement (16:9 default)

## Integration Pipeline

```
User Prompt
    ↓
Script Generator (Current Module)
    ↓
Structured JSON Script
    ↓
Visual Generation → Stable Diffusion
    ↓
Audio Synthesis → XCodec2/LLaSA3B
    ↓
Video Assembly
```

## Best Practices

1. **Prompt Engineering**:
   - Use clear technical descriptors ("cinematic wide shot", "semi-realistic")
   - Specify motion states explicitly ("drifting with motion blur")
   - Include negative prompts ("avoid blurry edges, unrealistic physics")

2. **Temporal Design**:
   - Maintain 5-second segments for smooth transitions
   - Use seed inheritance for visual continuity
   - Sync emotional peaks with visual climaxes

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Open Pull Request

## License

MIT License - See [LICENSE](LICENSE) for details
```

This README provides comprehensive documentation while maintaining technical specificity. It aligns with the project's structure and includes all critical aspects of the implementation.
