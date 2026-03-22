#!/usr/bin/env python3
"""AI Image Generation tool for claude2video pipeline.

Simple executor: reads assets.json (with Planner-generated prompts),
calls Google Gemini API, saves images.

Usage:
    python gen_images.py <assets.json> <output_dir>
"""

import argparse
import json
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("ERROR: google-genai package not found. Install with: pip install google-genai")
    sys.exit(1)

from PIL import Image
import io
import os

MODEL = "gemini-2.5-flash-image"


def generate_image(client, prompt, output_path, retry=2):
    """Call Gemini API to generate an image and save it.

    Parameters
    ----------
    client : genai.Client
        The Gemini API client.
    prompt : str
        The generation prompt (from Planner, used as-is).
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

            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image_data = part.inline_data.data
                    img = Image.open(io.BytesIO(image_data))

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


def main(assets_json_path, output_dir):
    """Generate images from Planner-provided prompts in assets.json.

    Parameters
    ----------
    assets_json_path : str
        Path to assets.json (output of Planner Phase 3).
    output_dir : str
        Output directory for generated images (usually output/{topic}/assets/).
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY environment variable not set.")
        print("Get an API key at https://aistudio.google.com/apikey")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    with open(assets_json_path, "r", encoding="utf-8") as f:
        assets_data = json.load(f)

    images = assets_data.get("images", [])
    if not images:
        print("No images to generate.")
        return

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "model": MODEL,
        "assets": [],
    }

    print(f"\nGenerating {len(images)} images concurrently...")

    def gen_image(spec):
        keyword = spec["keyword"]
        prompt = spec["prompt"]
        filename = spec.get("filename", f"{keyword}/{keyword}.png")
        asset_path = output_dir / filename

        print(f"\n  Image: {keyword}")
        success = generate_image(client, prompt, asset_path)
        return {
            "keyword": keyword,
            "prompt": prompt,
            "context": spec.get("context", ""),
            "path": str(asset_path.relative_to(output_dir)),
            "success": success,
        }

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(gen_image, spec): spec for spec in images}
        for future in as_completed(futures):
            manifest["assets"].append(future.result())

    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"\nManifest saved to {manifest_path}")
    print(f"Success: {sum(1 for a in manifest['assets'] if a['success'])}/{len(manifest['assets'])}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate images from Planner-provided prompts (assets.json)"
    )
    parser.add_argument("assets_json", help="Path to assets.json")
    parser.add_argument("output_dir", help="Output directory for images")
    args = parser.parse_args()
    main(args.assets_json, args.output_dir)
