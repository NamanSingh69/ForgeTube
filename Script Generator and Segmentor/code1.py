import json
import re
import google.generativeai as genai
from typing import Dict, List, Optional

class VideoScriptGenerator:
    """
    A robust video script generation system using Gemini API with:
    - Structured JSON output with validation
    - Multi-stage generation process
    - Feedback-based refinement
    - Comprehensive error handling
    """
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
        
        self.system_prompt_initial = """You are a professional video script generator for educational and marketing content.  Your task is to generate a detailed outline and initial draft for a video script, focusing on content and structure, *but not yet segmented into precise timestamps*.  Provide the core narration text and visual descriptions, which will be refined later.

        Output a JSON structure with these keys, but *without timestamps, speed, pitch, or detailed visual parameters* (these will be added in a later stage):

        {
            "topic": "Topic Name",
            "overall_narrative": "A concise summary of the entire video's storyline.",
            "key_sections": [
                {
                    "section_title": "Descriptive title for this section",
                    "narration_text": "The complete text to be spoken in this section.",
                    "visual_description": "A general description of the visuals for this section (e.g., 'Animation showing neural network layers', 'Footage of a doctor using medical imaging software')."
                }
            ]
        }
        """

        self.system_prompt_segmentation = """You are a professional video script segmenter.  Your task is to take an existing video script draft (provided in JSON format) and break it down into precise, timestamped segments for both audio and visuals, adhering to strict formatting and parameter guidelines.

        Input JSON Structure (from previous stage):

        {
            "topic": "Topic Name",
            "overall_narrative": "...",
            "key_sections": [
                {
                    "section_title": "...",
                    "narration_text": "...",
                    "visual_description": "..."
                }
            ]
        }
        
        Output JSON Structure (with all required fields):

        {
            "topic": "Topic Name",
            "audio_script": [{
                "timestamp": "00:00",
                "text": "Narration text",
                "speaker": "default|narrator_male|narrator_female",
                "speed": 0.9-1.1,
                "pitch": 0.9-1.2,
                "emotion": "neutral|serious|dramatic|mysterious|informative"
            }],
            "visual_script": [{
                "timestamp": "00:00",
                "prompt": "Detailed Stable Diffusion prompt",
                "negative_prompt": "Low quality elements to avoid",
                "style": "realistic|cinematic|hyperrealistic|fantasy|scientific",
                "guidance_scale": 11.0-14.0,
                "steps": 50-100,
                "seed": 6-7 digit integer,
                "width": 1024,
                "height": 576
            }]
        }

        Rules for Segmentation:
        
        1. Break down the `narration_text` and `visual_description` from the input JSON into smaller segments, each approximately 5-10 seconds long.
        2. Generate timestamps ("00:00", "00:05", "00:10", etc.) for each segment in both `audio_script` and `visual_script`.
        3.  Maintain strict synchronization:  The `timestamp` values *must* be identical for corresponding audio and visual segments.
        4.  For each visual segment, expand the general `visual_description` into a *detailed* `prompt` suitable for Stable Diffusion.  Include a corresponding `negative_prompt`.
        5.  Choose appropriate values for `speaker`, `speed`, `pitch`, and `emotion` for each audio segment.
        6.  Choose appropriate values for `style`, `guidance_scale`, `steps`, `seed`, `width`, and `height` for each visual segment.
        7. Ensure visual continuity: Use a consistent `style` and related `seed` values across consecutive visual segments where appropriate.  Vary the seed to introduce changes, but maintain a logical flow.
        8.  Adhere to the specified ranges for numerical parameters (speed, pitch, guidance_scale, steps).
        9. Validate JSON structure before output

        """
    
    # Handling API calls
    def _generate_content(self, prompt: str, system_prompt: str) -> str:
        try:
            response = self.model.generate_content(
                contents=[system_prompt, prompt]
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"API call failed: {str(e)}")
    
    # JSON extraction with multiple fallback strategies
    def _extract_json(self, raw_text: str) -> Dict:
        try:
            # First try direct parsing
            return json.loads(raw_text)
        except json.JSONDecodeError:
            try:
                # Attempt to extract JSON from markdown
                json_match = re.search(r'```json\n(.*?)\n```', raw_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
                # Fallback to bracket matching
                json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                return json.loads(json_match.group()) if json_match else {}
            except Exception as e:
                raise ValueError(f"JSON extraction failed: {str(e)}")
    
    # Validation of script structure and values (for the final, segmented script)
    def _validate_script(self, script: Dict) -> bool:
        required = {
            'audio_script': ['timestamp', 'text', 'speaker', 'speed', 'pitch', 'emotion'],
            'visual_script': ['timestamp', 'prompt', 'negative_prompt', 'style',
                             'guidance_scale', 'steps', 'seed', 'width', 'height']
        }
        
        for section, fields in required.items():
            if section not in script:
                raise ValueError(f"Missing section: {section}")
            for item in script[section]:
                for field in fields:
                    if field not in item:
                        raise ValueError(f"Missing field '{field}' in {section}")
                    
                # Validate parameter ranges
                if section == 'audio_script':
                    if not 0.9 <= item['speed'] <= 1.1:
                        raise ValueError("Speed must be between 0.9-1.1")
                elif section == 'visual_script':
                    if not 7.0 <= item['guidance_scale'] <= 12.0:
                        raise ValueError("Guidance scale must be between 7.0-12.0")
        
        return True

    # Generates a complete video script with synchronized audio/visual elements
    def generate_script(self, topic: str, duration: int = 60,
                       key_points: Optional[List[str]] = None) -> Dict:
        # Stage 1: Initial Script Generation
        initial_prompt = f"""Generate an initial video script outline for a {duration}-second video about: {topic}
        Key Points: {key_points or 'Comprehensive coverage'}
        Focus on the overall narrative and key sections, but do *not* include timestamps or detailed technical parameters yet."""

        raw_initial_output = self._generate_content(initial_prompt, self.system_prompt_initial)
        initial_script = self._extract_json(raw_initial_output)

        # Stage 2: Segmentation and Detailed Parameterization
        segmentation_prompt = f"""
        Here is the initial script draft:
        {json.dumps(initial_script, indent=2)}

        Now, segment this script into 5-10 second intervals, adding timestamps and all required audio/visual parameters.  The total duration should be approximately {duration} seconds.
        """

        raw_segmented_output = self._generate_content(segmentation_prompt, self.system_prompt_segmentation)
        segmented_script = self._extract_json(raw_segmented_output)

        # Add the topic from the initial script to segmented script
        segmented_script['topic'] = initial_script['topic']

        self._validate_script(segmented_script)  # Validate the *segmented* script
        return segmented_script

    # Iteratively improve an existing script based on user feedback
    def refine_script(self, existing_script: Dict, feedback: str) -> Dict:
        prompt = f"""Refine this script based on feedback:
        Existing Script: {json.dumps(existing_script, indent=2)}
        Feedback: {feedback}
        Requirements:
        - Maintain JSON structure
        - Preserve valid parameters
        - Ensure timestamp continuity"""
        
        raw_output = self._generate_content(prompt, self.system_prompt_segmentation)
        refined_script = self._extract_json(raw_output)
        self._validate_script(refined_script)
        return refined_script

    def save_script(self, script: Dict, filename: str) -> None:
        """Save validated script to file with indentation"""
        with open(filename, 'w') as f:
            json.dump(script, f, indent=2)

# Example Usage
if __name__ == "__main__":
    generator = VideoScriptGenerator(api_key="AIzaSyCszqTt8bYM1mkwqF0DInV6CCwsFUA1_7M")

    try:
        script = generator.generate_script(
            topic="Neural Networks in Medical Imaging",
            duration=90,
            key_points=["Diagnosis accuracy", "Pattern recognition", "Case studies"]
        )
        print("Initial Script:")
        print(json.dumps(script, indent=2))

        feedback = input("Please provide feedback on the script (or type 'no' to skip refinement): ")

        if feedback.lower() != "no":
            refined_script = generator.refine_script(script, feedback)
            print("\nRefined Script:")
            print(json.dumps(refined_script, indent=2))
            generator.save_script(refined_script, "refined_medical_ai_script.json")
        else:
            generator.save_script(script, "medical_ai_script.json")

    except Exception as e:
        print(f"Script generation failed: {str(e)}")