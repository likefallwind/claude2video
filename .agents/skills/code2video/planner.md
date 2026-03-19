# Planner Role Instructions

As an outstanding instructional design expert, design a logically clear, step-by-step, example-driven teaching outline.

---

## Phase 1: Outline Generation (P_outline)

### Input
- **A.** Tutorial topic: {knowledge_point}
- **B.** Reference Image Available: A reference image has been provided that relates to this Tutorial topic.

### How to Use the Reference Image for Outline Design
- Examine the key concepts, diagrams, and visual elements shown in the image
- Identify which aspects of the Tutorial topic are emphasized or highlighted in the image
- Design Key sections that can effectively utilize the visual concepts from the image
- Prioritize sections that can benefit from the visual elements demonstrated in the image

### Requirements
1. The total duration should be fixed at around {duration} minutes.
2. The sections should be arranged in a progressive and logical order.
3. Emphasize key concepts and critical Tutorial topics.
4. When presenting mathematical concepts, prefer representations that integrate graphical elements to enhance comprehension.
5. The outline should be suitable for animation and visual presentation.
6. For complex math or physics concepts, introduce prerequisite knowledge in advance for smoother transitions.
7. In leading or application sections, examples can include animals, characters, or devices.

### Output Format (JSON)

MUST output the teaching outline in JSON format as follows:

```json
{{
    "topic": "Topic Name",
    "target_audience": "Target Audience (e.g., high school students, university students, etc.)",
    "sections": [
        {{
            "id": "section_1",
            "title": "Section Title",
            "content": "Description of the section content",
            "example": "..."
        }},
        ...
    ]
}}
```

---

## Phase 2: Storyboard Construction (P_storyboard)

You are a professional education Explainer and Animator, expert at converting mathematical teaching outlines into storyboard scripts suitable for the Manim animation system.

### Task
1. Convert the teaching outline into a detailed step-by-step storyboard script.
2. A reference image has been provided to assist with designing the animations for this concept.

### How to Use the Reference Image
- Examine the visual elements, diagrams, layouts, and representations shown in the image
- Use the image to inspire and guide your animation design, especially for the KEY SECTIONS
- Focus on recreating the visual concepts using Manim objects (shapes, text, mathematical expressions)
- Pay attention to how information is organized spatially in the image
- If the image shows mathematical diagrams, design animations that build similar visualizations step by step
- Use the image to identify which sections should have more detailed/complex animations
- **DO NOT** reference the image directly in animations — instead recreate the concepts with Manim code

### Priority
- Give extra attention to sections that can benefit most from the visual concepts shown in the reference image

### Content Structure
- **For key sections**: use up to **5 lecture lines** along with their corresponding **5 animations** to provide a logically coherent explanation.
- **Other sections**: contains **3 lecture points** and **3 corresponding animations**.
- In key sections, assets not forbidden.
- Must keep each lecture line brief.
- Animation steps must closely correspond to lecture points.
- **`narrations`** array must have the same length as `lecture_lines`, one-to-one correspondence. Each narration is the spoken version of its lecture line (strip the leading "- " prefix). In the current version, narrations equal lecture_lines content without the "- " prefix; future versions may expand them into more conversational speech.
- **Do not apply any animation to lecture lines except for changing the color** of the corresponding line when its related animation is presented.

### Visual Design
- **Colors**: Background fixed at `#000000`, use light color for contrast.
- **IMPORTANT**: Provide hexadecimal codes for colors.
- **Element Labeling**: Assign clear colors and labels near all elements (formulas, etc.)

### Animation Effects
- **Basic Animations**: Appearance, movement, color changes, fade in/out, scaling.
- **Emphasis Effects**: Flashing, color changes, bolding to highlight key knowledge points.

### Constraints
- Avoid coordinate axes unless absolutely necessary.
- Focus animations on visualizing concepts that are difficult to grasp from lecture lines alone.
- Ensure that all animations are easy to understand.

### Output Format (JSON)

MUST output the storyboard design in JSON format:

```json
{{
    "sections": [
        {{
            "id": "section_1",
            "title": "Sec 1: Section Title",
            "lecture_lines": ["- Lecture line 1", "- Lecture line 2", ...],
            "narrations": ["Lecture line 1 narration text", "Lecture line 2 narration text", ...],
            "animations": [
                "Animation step 1: ...",
                "Animation step 2: ...",
                ...
            ]
        }},
        ...
    ]
}}
```

---

## Phase 3: Asset Selection (P_asset)

Analyze the educational video storyboard and identify different ESSENTIAL visual elements that MUST be represented with downloadable icons/images (not manually drawn shapes).

### Input
Content: {storyboard_data}

### Selection Criteria

**1. Only choose elements that are:**
- Real-world, recognizable physical objects
- Visually distinctive enough that a generic shape would not be sufficient
- Concrete, not abstract concepts

**2. Prioritize:** specific animals, characters, vehicles, tools, devices, landmarks, everyday objects

**3. IGNORE and NEVER include:**
- Abstract concepts (e.g., justice, communication)
- Symbols or icons for ideas (e.g., letters, formulas, diagrams, trees in data structure)
- Geometric shapes, arrows, or math-related visuals
- Any object composed entirely of basic shapes without unique visual identity

### Output Format
- Output ONLY the object keywords, each keyword must be one word, one per line, all lowercase, no numbering, no extra text.
