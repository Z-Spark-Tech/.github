# Z-Spark Tech — Animated GitHub Banner

A complete, editable source project for the Z-Spark Tech animated GitHub organization banner.

The project includes the original Z-Spark logo supplied for this design, the dark charcoal-and-red background artwork, the Python generator, the finished looping GIF, a still preview, and a ready-to-upload GitHub organization profile README.

## Final banner

- **Canvas:** 1600 × 500 px
- **Animation:** 36 frames, 100 ms per frame
- **Loop:** Infinite
- **Duration:** 3.6 seconds per loop
- **Format:** GIF

The supplied logo artwork is preserved. The generator trims transparent margins and resizes the logo proportionally; the animated highlight is masked to the logo's existing alpha channel. The typography, border pulse, red ribbon glow, and circuit-node pulses are composited as separate layers.

## Project structure

```text
Z-Spark-Tech-Animated-Banner-Project/
├── assets/
│   ├── z-spark-logo-original.png
│   └── z-spark-dark-tech-background.png
├── src/
│   └── build_banner.py
├── output/
│   ├── Z-Spark-Tech-Animated-GitHub-Banner.gif
│   ├── Z-Spark-Tech-Animated-GitHub-Banner-Preview.png
│   └── frame-contact-sheet.png
├── github-profile/
│   └── profile/
│       ├── README.md
│       └── assets/
│           └── Z-Spark-Tech-Animated-GitHub-Banner.gif
├── requirements.txt
└── README.md
```

## Rebuild the banner

Requires Python 3.10 or newer.

```bash
python -m venv .venv
```

Activate the virtual environment, then install dependencies:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

python -m pip install -r requirements.txt
python src/build_banner.py
```

The script regenerates the GIF, preview PNG, and frame contact sheet in `output/`.

## Publish the organization profile on GitHub

GitHub displays an organization profile README from a **public** repository named `.github`, using the file `profile/README.md`.

1. Create a public repository named `.github` under the `Z-Spark-Tech` organization.
2. Copy the contents of `github-profile/profile/` into that repository's `profile/` directory.
3. Keep the `assets/` folder beside `README.md` so its relative image path remains valid.
4. Commit the files to the default branch.
5. Open the organization Overview and check **View as: Public**.

The package does not change repository visibility or publish anything to GitHub automatically.

## Embed the GIF elsewhere

```markdown
![Z-Spark Tech animated banner](assets/Z-Spark-Tech-Animated-GitHub-Banner.gif)
```

## Customize

Open `src/build_banner.py`. The canvas dimensions, frame count, frame duration, logo scale, text, colors, animation path, and glow strengths are defined near the top of the file or in `build_frames()`.

The background and logo are replaceable files in `assets/`. Keep the logo as a transparent PNG for the cleanest result.
