# Pixel Palette Generator

Generate mesmerizing pixel art locally or in the browser by sampling each pixel from curated or custom color palettes. The repository ships both a Python CLI and a fully client-side web app deployed through GitHub Pages.

## Features

- Deterministic results with optional seeds
- Built-in palettes: black & white, grayscale, or the entire 24-bit spectrum
- Custom palette support with familiar hex notation (`#RGB` and `#RRGGBB`)
- Row-major rendering so progress is visible while images are created
- CLI progress logging and large-image confirmations (`--yes` to skip)
- Browser app with responsive UI, cancel controls, and downloadable PNG output

## Getting started

### Requirements

- Python 3.10+
- [Pillow](https://python-pillow.org/) (install via `pip install -r requirements.txt`)
- Optional: NumPy for faster experimentation (install via `pip install .[extras]`)

### Install & use the CLI

```bash
pip install -r requirements.txt
pip install .
pixelgen --mode random --size 1080x1920 --palette bw --outfile bw.png
pixelgen --mode random --size 512x512 --palette all --seed 42 --outfile all.png
pixelgen --mode random --size 720x1280 --colors "#75151E,#49678D,#3E3B32" --outfile custom.png
pixelgen --mode custom --size 256x256 --colors "#ff0044,#00ffaa,#1800ff" --outfile from_prompt.png
```

CLI tips:

- Use `--format` to force PNG/JPG/BMP regardless of file extension.
- Supply `--progress` to print row milestones while rendering.
- If the size exceeds 50 million pixels, the CLI will ask for confirmation unless `--yes` is provided.
- To capture your own screenshots for documentation, generate a small image (for example, `pixelgen --mode random --size 64x64 --palette bw --outfile docs-sample.png`) and include it after pushing the repository.

### Web app (GitHub Pages)

The web interface lives in [`web/`](web/) and is published automatically to GitHub Pages via the included workflow. Once GitHub Pages is enabled for the repository, your app will be available at:

```
https://<your-github-username>.github.io/pixel-palette-generator/
```

Controls include:

- Size (`WIDTHxHEIGHT`), mode (`random` or `custom`), palette radios, custom colors, and optional seed
- Generate button to start rendering with responsive row-by-row updates
- Cancel button to abort a run midstream
- Download PNG button enabled after a successful render
- Inline validation messages and large-image warnings (with confirmation dialogs)

### GitHub Pages deployment

The workflow at [`.github/workflows/pages.yml`](.github/workflows/pages.yml) publishes the `web/` directory automatically whenever you push to the `main` branch. To complete setup:

1. In the repository settings open **Pages**.
2. Set **Build and deployment** to **GitHub Actions** (if it is not already).
3. Push to `main`. The workflow uploads the static assets and deploys them to Pages.

#### First-time push & deploy checklist

If the project has not yet been pushed to GitHub, follow these steps from your local clone to wire up the remote repository and trigger the Pages deployment:

1. **Create the empty repository on GitHub.** On <https://github.com/new> enter `pixel-palette-generator` as the name and leave it blank (no README/License) so that you can push the existing history from this folder.
2. **Open a terminal at the project root** (the directory containing this README) and run one of the following remote commands, depending on whether you prefer SSH or HTTPS:

   ```bash
   # SSH (requires SSH keys set up with GitHub)
   git remote add origin git@github.com:<your-username>/pixel-palette-generator.git

   # or HTTPS
   git remote add origin https://github.com/<your-username>/pixel-palette-generator.git
   ```

3. **Ensure the main branch is named correctly and push:**

   ```bash
   git branch -M main
   git push -u origin main
   ```

4. **Confirm the remote is connected** (optional but reassuring):

   ```bash
   git remote -v
   ```

After the push completes, GitHub Actions automatically runs the Pages workflow. Monitor the deployment progress under **Actions → Deploy web app to GitHub Pages**. When the workflow finishes, the static site will be available at `https://<your-github-username>.github.io/pixel-palette-generator/`.

If you run into authentication prompts during `git push`, GitHub provides detailed guides for [configuring SSH keys](https://docs.github.com/authentication/connecting-to-github-with-ssh) and [creating personal access tokens for HTTPS pushes](https://docs.github.com/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).

### Testing

Run the unit tests with:

```bash
pytest
```

Tests cover size parsing, hex color normalization, and a CLI smoke test that ensures generated pixels always belong to the active palette (skipped automatically if Pillow is unavailable).

### Performance & determinism

- Rendering occurs row-by-row so you can monitor progress in both CLI and web UI.
- `--seed` (CLI) and the seed input (web) ensure reproducible outputs.
- Extremely large images can be memory intensive; heed the warnings or pass `--yes`/confirm when you understand the trade-offs.

### License

Released under the [MIT License](LICENSE).
