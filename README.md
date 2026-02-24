# Lynn Resume Website

Static single-page resume website for GitHub Pages.

## Regenerate resume data from PDF

The resume content is sourced from `lynnresumepdf.pdf` and converted into `assets/resume.json`.

```bash
python scripts/extract_resume.py
```

No external dependencies are required; the script uses Python's standard library.

## Preview locally

From the repository root:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Deploy on GitHub Pages

1. Push this repository to GitHub.
2. In **Settings → Pages**, choose **Deploy from branch**.
3. Select the `main` branch and root (`/`) folder.
4. Save; GitHub Pages serves `index.html` from repo root.

All links use relative paths and work on GitHub Pages.
