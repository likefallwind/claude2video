#!/usr/bin/env python3
"""AI Image Generation tool for claude2video pipeline.

Generates educational asset images and section illustrations using
Google Gemini Image API. Reads storyboard.json + assets.txt and
outputs images to the assets/ directory.

Usage:
    python gen_images.py <storyboard.json> <assets.txt> <output_dir> [--section-illustrations]
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("ERROR: google-genai package not found. Install with: pip install google-genai")
    sys.exit(1)

from PIL import Image
import io
import os

MODEL = "gemini-3.1-flash-image-preview"  # image generation capable model


def build_asset_prompt(keyword, section_context, topic):
    """Build a detailed prompt for generating an asset icon image.

    Parameters
    ----------
    keyword : str
        The asset keyword (e.g., "basketball", "microscope").
    section_context : str
        Animation description context from the storyboard.
    topic : str
        The overall video topic.

    Returns
    -------
    str
        A prompt string for the image generation API.
    """
    return (
        f"Clean flat vector illustration of {keyword}, educational style, "
        f"simple clear silhouette, white or transparent background, "
        f"suitable for math/science teaching video about {topic}. "
        f"Context: {section_context}. "
        f"No text, no labels, no watermarks. Centered composition."
    )


def build_illustration_prompt(section, topic):
    """Build a prompt for generating a section illustration.

    Parameters
    ----------
    section : dict
        A section object from storyboard.json with 'title', 'lecture_lines', 'animations'.
    topic : str
        The overall video topic.

    Returns
    -------
    str
        A prompt string for the section illustration.
    """
    title = section.get("title", "")
    lines = section.get("lecture_lines", [])
    content_summary = "; ".join(line.lstrip("- ").strip() for line in lines[:3])

    return (
        f"Soft educational illustration for '{title}': {content_summary}. "
        f"Topic: {topic}. "
        f"Style: clean vector art, suitable as background visual element, "
        f"muted colors, subtle and elegant, no text, no labels. "
        f"16:9 aspect ratio, 1K resolution."
    )


def generate_image(client, prompt, output_path, retry=2):
    """Call Gemini API to generate an image and save it.

    Parameters
    ----------
    client : genai.Client
        The Gemini API client.
    prompt : str
        The generation prompt.
    output_path : str or Path
        Where to save the generated PNG.
    retry : int
        Number of retry attempts on failure.

    Returns
    -------
    bool
        True if image was saved successfully.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    for attempt in range(retry + 1):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )

            # Extract image from response parts
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image_data = part.inline_data.data
                    img = Image.open(io.BytesIO(image_data))

                    # Convert to RGBA PNG
                    if img.mode != "RGBA":
                        img = img.convert("RGBA")

                    img.save(str(output_path), "PNG")
                    print(f"  Saved: {output_path}")
                    return True

            print(f"  Warning: No image in response for '{output_path.stem}'")
            if attempt < retry:
                print(f"  Retrying ({attempt + 1}/{retry})...")

        except Exception as e:
            print(f"  Error generating image: {e}")
            if attempt < retry:
                print(f"  Retrying ({attempt + 1}/{retry})...")

    print(f"  FAILED: Could not generate {output_path}")
    return False


def parse_assets_file(assets_path):
    """Parse assets.txt into a list of keywords.

    Supports both plain keywords and 'keyword: description' format.

    Parameters
    ----------
    assets_path : str or Path
        Path to assets.txt.

    Returns
    -------
    list[dict]
        Each dict has 'keyword' and optional 'description'.
    """
    assets = []
    with open(assets_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                keyword, desc = line.split(":", 1)
                assets.append({
                    "keyword": keyword.strip().lower(),
                    "description": desc.strip(),
                })
            else:
                assets.append({
                    "keyword": line.lower(),
                    "description": "",
                })
    return assets


def main(storyboard_path, assets_path, output_dir, section_illustrations=False):
    """Main orchestration: generate asset images and optional section illustrations.

    Parameters
    ----------
    storyboard_path : str
        Path to storyboard.json.
    assets_path : str
        Path to assets.txt.
    output_dir : str
        Output directory for generated images (usually output/{topic}/assets/).
    section_illustrations : bool
        Whether to also generate per-section illustrations.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY environment variable not set.")
        print("Get an API key at https://aistudio.google.com/apikey")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    # Load storyboard
    with open(storyboard_path, "r", encoding="utf-8") as f:
        storyboard = json.load(f)

    topic = storyboard.get("topic", "educational video")
    sections = storyboard.get("sections", [])

    # Build context map: keyword -> relevant animation descriptions
    context_map = {}
    for section in sections:
        anims = section.get("animations", [])
        context = "; ".join(anims[:2]) if anims else section.get("title", "")
        for anim in anims:
            # Extract keywords mentioned in animations for context matching
            for asset in parse_assets_file(assets_path) if Path(assets_path).exists() else []:
                if asset["keyword"] in anim.lower():
                    context_map[asset["keyword"]] = context

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "model": MODEL,
        "topic": topic,
        "assets": [],
        "illustrations": [],
    }

    # --- Generate asset images ---
    if Path(assets_path).exists():
        assets = parse_assets_file(assets_path)
        print(f"\nGenerating {len(assets)} asset images...")

        for asset in assets:
            keyword = asset["keyword"]
            desc = asset.get("description", "")
            context = context_map.get(keyword, desc)

            prompt = build_asset_prompt(keyword, context, topic)
            asset_dir = output_dir / keyword
            asset_path = asset_dir / f"{keyword}.png"

            print(f"\n  Asset: {keyword}")
            success = generate_image(client, prompt, asset_path)

            manifest["assets"].append({
                "keyword": keyword,
                "prompt": prompt,
                "path": str(asset_path.relative_to(output_dir)),
                "success": success,
            })
    else:
        print(f"Warning: assets file not found at {assets_path}")

    # --- Generate section illustrations ---
    if section_illustrations:
        print(f"\nGenerating {len(sections)} section illustrations...")

        for section in sections:
            section_id = section.get("id", "unknown")
            prompt = build_illustration_prompt(section, topic)
            illust_dir = output_dir / section_id
            illust_path = illust_dir / "illustration.png"

            print(f"\n  Illustration: {section_id}")
            success = generate_image(client, prompt, illust_path)

            manifest["illustrations"].append({
                "section_id": section_id,
                "prompt": prompt,
                "path": str(illust_path.relative_to(output_dir)),
                "success": success,
            })

    # Write manifest
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"\nManifest saved to {manifest_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate educational asset images using Gemini Image API"
    )
    parser.add_argument("storyboard", help="Path to storyboard.json")
    parser.add_argument("assets", help="Path to assets.txt")
    parser.add_argument("output_dir", help="Output directory for images")
    parser.add_argument(
        "--section-illustrations",
        action="store_true",
        help="Also generate per-section illustrations",
    )
    args = parser.parse_args()
    main(args.storyboard, args.assets, args.output_dir, args.section_illustrations)
