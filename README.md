# StudySpace · Field Notes Edition

A cozy, student-focused, DocHub-inspired PDF workspace built with **Streamlit** and **PyMuPDF**. This redesign uses cream, linen, sage, butter, oat, and clay tones instead of the previous purple or blue themes.

## Getting started in VS Code (Windows)

1. Download `studyspace_granola.zip` into your **Downloads** folder.
2. Open **VS Code → Terminal → New Terminal**. If you have an old Streamlit server running, press **Ctrl + C** in that terminal to stop it first.
3. Copy and run **only the commands** below, one at a time. Do not copy the `(.venv) PS C:\...>` text shown before your cursor.

```powershell
cd "C:\Users\jacke\OneDrive\Desktop\proj_prog"
Expand-Archive -Path "$HOME\Downloads\studyspace_granola.zip" -DestinationPath "." -Force
cd .\studyspace_granola
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The app should open at **http://localhost:8501**. If `python` isn't recognized, try replacing `python` with `py` in the last two commands. A correctly configured virtual environment can be used as usual.

**Easy launch next time:** Open the extracted `studyspace_granola` folder and double-click `launch_studyspace.bat` (after libraries are installed). It runs `app.py` from the right directory.

## Features

- **Big PDF reading canvas:** PDF is centered and fills its editor; **Full-width paper** hides the inspector if you need more room.
- **Voice studio:** Choose and preview voices available in Chrome or Edge; adjust speech speed and pitch. Browser voices vary by system and device.
- **Speech follow-along:** Select **Read + follow**. The spoken chunk is softly highlighted **sage**, with the current word highlighted **butter-yellow** in browsers that provide word-boundary events. Pause, resume and stop anytime. Reading follows the *current page*.
- **Movable Post-it-style notes:** Select **Place note** above the PDF, pick Butter, Sage, Clay, or Oat, then click the paper. Type in the note, drag its top strip to reposition, or use the × button to delete. The drag handle is also keyboard-operable using arrow keys.
- **Permanent PDF highlights:** In **Highlight**, type a word or phrase and choose a color. Apply to the current page or the full document.
- **PDF export:** Download the document with visible notes printed on the paper and highlights preserved as annotations. The complete note text is also saved in the PDF comments.
- **Optional WAV:** The **Audio** panel also has a WAV generator using your local `pyttsx3` engine. It uses the operating system's voice, which may sound different from your selected browser voice.
- **Your original comments:** The comments from the first Python prototype remain in `app.py` for documenting the project's development.

## Important limitations

- The browser's built-in voices are free but may not be natural neural voices; voice availability depends on Chrome/Edge and Windows. This version does not make external paid speech API calls.
- Sentence/chunk follow-along works where browser speech synthesis works; **word-by-word timing varies with browser and selected voice**.
- Sticky notes and highlights are kept in Streamlit session state until you close/reload the session. **Download your annotated PDF to keep your work.** Exported PDF notes appear on pages but cannot be re-imported as draggable HTML stickies automatically.
- Scanned or image-only PDFs will display but need OCR for speech and typed-phrase highlighting.
- Annotation highlight uses a typed word or phrase, not dragging your mouse over the underlying PDF text.
- Placing sticky notes over existing paragraphs can cover parts of the page, like physical sticky notes.
- PDF upload is processed in the Streamlit app running on your computer; make sure not to deploy private PDFs to an untrusted server.

## Project files

- `app.py` — complete Streamlit app, styling, sidebar, PDF tools and original comments
- `editor/index.html` — interactive PDF page, browser speech, synchronized highlights, Post-it notes, zoom and keyboard support
- `reader.py` — PDF image rendering and word positions for follow-along speech
- `pdf_tools.py` — PDF extraction, phrase highlights and sticky-note PDF export
- `sample_reading.pdf` — a two-page granola-themed test document
- `.streamlit/config.toml` — matching warm-light Streamlit theme
- `requirements.txt` — install dependencies
- `launch_studyspace.bat` — Windows launcher
- `design_preview.png` — preview of the interactive PDF editor

## Troubleshooting

- **Can't type in terminal:** Press **Ctrl + C** if Streamlit is still running. Or choose **Terminal → New Terminal**.
- **`requirements.txt` not found:** Run `dir` and confirm you are inside `studyspace_granola`.
- **No sound:** Click **Preview voice**, check your system output volume, try Chrome/Edge, and choose a different voice. Browser speech may be blocked until you click the playback button.
- **PDF page blank:** Try the included sample first. A password-protected or damaged PDF won't load. For scanned documents, visual rendering may work but reading text will not.
