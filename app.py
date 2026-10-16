"""StudySpace · Field Notes Edition — accessible PDF reader and stationery workspace.

Run: python -m streamlit run app.py

The original Accessible PDF Reader comments are preserved in this file.
"""

import tempfile  # creates a temporary file
import os  # used to check if the temp file exists
import html  # prevents study notes from being interpreted as HTML
import json  # passes saved highlights and notes to the PDF exporter
import hashlib  # keeps each uploaded PDF's notes separate
from pathlib import Path  # finds the sample PDF and editor assets

import streamlit as st  # this creates the web app interface
import streamlit.components.v1 as components  # allows real drag-and-drop notes on PDFs
# brings in the pdf colors and functions for opening, marking, and saving files
from pdf_tools import PALETTE, NOTE_COLORS, pdf_info, count_matches, annotated_pdf, render_page
from reader import page_visual_and_segments  # spoken-word positions on PDF pages

# pyttsx3 # text-to-speech conversion library
# The optional WAV downloader uses pyttsx3. For the live Read Aloud feature,
# we now use the browser so students can choose a voice and see spoken words.

# this is where i set up how the website opens
# 1) add titles
# sets the basic settings for the studyspace webpage
st.set_page_config(
    # set up a title
    # this is the name that shows up in the browser tab
    page_title="StudySpace | Your little reading nook",
    # adds the notebook icon next to the website name
    page_icon="📓",
    # makes the page wide so the pdf has more space
    layout="wide",
    # keeps the sidebar closed when the website first opens
    initial_sidebar_state="collapsed",
)

# this is the styling for the overall website and its colors
st.markdown("""
<style>
/* StudySpace · Field Notes Edition: calm granola palette with an editorial, paper-and-ink feel. */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Fraunces:opsz,wght,SOFT,WONK@9..144,500,35,1;9..144,600,35,1;9..144,700,35,1&display=swap');
:root {--ink:#38382e;--muted:#746e61;--cream:#f6f2e9;--linen:#ede7da;--paper:#fffdf8;--line:#dcd4c3;--sage:#71836a;--dark-sage:#4e674f;--clay:#b8745c;--oat:#e5d4ae;--butter:#f2df9e;}
html,body,[data-testid="stApp"] {font-family:'DM Sans',Verdana,sans-serif;color:var(--ink);}
.stApp{background:#f5f0e6;background-image:radial-gradient(#ddd2c0 0.8px, transparent 0.8px);background-size:23px 23px;}
[data-testid="stHeader"]{background:transparent;height:2.5rem;}
.block-container{max-width:2200px;padding:.65rem 1.6rem 2.7rem;}
[data-testid="stSidebar"]{background:#ebe7dc;}
h1,h2,h3{font-family:'Fraunces',Georgia,serif;color:#3f463a;}
small,[data-testid="stCaptionContainer"]{color:#6b6b5f!important;}
[data-testid="stExpander"]{background:#fffcf5;border:1px solid #d9d0be;border-radius:15px;box-shadow:0 2px 0 #ddd3c2;}
[data-testid="stVerticalBlockBorderWrapper"] > div:has(> [data-testid="stVerticalBlock"]){border:1px solid #ded5c5!important;border-radius:15px!important;background:#fffdf8!important;}
[data-testid="stTabs"] [data-baseweb="tab-list"]{background:#ece7db;border-radius:12px;padding:4px;gap:4px;}
[data-testid="stTabs"] button[role="tab"]{font-size:.79rem;font-weight:800;border-radius:9px;padding:.47rem .65rem;color:#625c4e;}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"]{background:#fdfbf5;color:#485c45;box-shadow:0 1px 5px #65594422;}
[data-testid="stTabs"] [data-baseweb="tab-highlight"],[data-testid="stTabs"] [data-baseweb="tab-border"]{display:none;}
[data-testid="stWidgetLabel"] p{font-size:.82rem;font-weight:700;color:#5f5d50;}
input,textarea{caret-color:#4f6d51;}
[data-baseweb="input"]>div,[data-baseweb="select"]>div,[data-baseweb="textarea"]>div{background:#fffefa!important;border-color:#dcd2bf!important;border-radius:10px!important;}
div.stButton > button,div.stDownloadButton > button,div.stFormSubmitButton > button{min-height:40px;border-radius:10px;border:1px solid #c9c5b3;background:#fffcf5;color:#485848;font-weight:800;box-shadow:0 2px 0 #e6dfd1;}
div.stButton > button:hover,div.stDownloadButton > button:hover,div.stFormSubmitButton > button:hover{border-color:#7e9277;background:#f0f5ec;color:#385a3d;}
div.stButton>button[kind="primary"],div.stDownloadButton>button[kind="primary"],div.stFormSubmitButton>button[kind="primary"]{background:#58735a;border-color:#58735a;color:#fffdf4;box-shadow:0 3px 0 #3e5743;}
div.stButton>button[kind="primary"]:hover,div.stDownloadButton>button[kind="primary"]:hover,div.stFormSubmitButton>button[kind="primary"]:hover{background:#47634c;color:white;}
:focus-visible {outline:3px solid #b77656!important;outline-offset:2px;}
/* Warm, illustrated masthead: not the default Streamlit dashboard look. */
.ss-header{position:relative;overflow:hidden;background:#fffaf0;border:1px solid #d5cbb8;border-radius:20px;margin:6px 0 13px;box-shadow:0 6px 0 #e5dccb,0 13px 25px #5c50391b;display:flex;gap:16px;justify-content:space-between;align-items:center;min-height:116px;padding:19px 29px;}
.ss-header:before{content:'';position:absolute;width:230px;height:220px;border-radius:50%;background:#e3eadb;right:13%;top:-171px;opacity:.65;}
.ss-header:after{content:'';position:absolute;width:145px;height:145px;border:1px solid #cfbaa2;border-radius:50%;right:-57px;bottom:-95px;opacity:.7;}
.ss-brand{display:flex;gap:18px;align-items:center;position:relative;z-index:1;}
.ss-icon{width:66px;height:67px;background:#e6dfc8;border:1px solid #cbbda3;border-radius:9px 16px 13px 7px;box-shadow:4px 5px 0 #bac8af,6px 8px 0 #e2d6c4;display:grid;place-items:center;font-size:34px;transform:rotate(-5deg);}
.ss-eyebrow{display:flex;align-items:center;gap:8px;color:#9b785f;text-transform:uppercase;letter-spacing:.21em;font-size:.61rem;font-weight:800;margin-bottom:6px;}
.ss-eyebrow::before{content:'';display:inline-block;width:21px;height:1px;background:#b9967a;}
.ss-name{font-family:'Fraunces',Georgia,serif;font-size:clamp(28px,3.2vw,43px);font-weight:700;color:#3f4c3c;letter-spacing:-.065em;line-height:1.02;}
.ss-name b{font-weight:700;color:#9b705a;}
.ss-sub{font-size:.8rem;color:#7a7567;font-weight:600;margin-top:7px;letter-spacing:.012em;}
.ss-right{display:flex;align-items:center;gap:9px;flex-wrap:wrap;z-index:1;}
.ss-tag{display:inline-flex;align-items:center;gap:7px;border:1px solid #d6d0bf;background:#f5f1e6;border-radius:99px;padding:8px 11px;color:#5d6b55;font-size:.72rem;font-weight:800;white-space:nowrap;}
.ss-tag.accent{background:#e8eee1;border-color:#ccd7c2;}
.ss-index{font-size:.66rem;font-weight:800;letter-spacing:.15em;color:#a4826a;margin-right:6px;text-transform:uppercase;}
.ss-file{background:#fffdf8;border:1px solid #d7cdbc;border-radius:16px;padding:11px 17px;display:flex;gap:15px;justify-content:space-between;align-items:center;flex-wrap:wrap;box-shadow:0 4px 0 #e9dfd1;margin:6px 0 13px;}
.ss-docname{font-size:.93rem;color:#44473c;font-weight:800;overflow-wrap:anywhere;}
.ss-detail{color:#847b6d;font-weight:600;font-size:.74rem;margin-top:4px;}
.ss-section{font-family:'Fraunces',Georgia,serif;font-size:1.18rem;font-weight:600;color:#454b3d;margin:12px 0 8px;}
.ss-muted{font-family:'DM Sans',Verdana,sans-serif;font-size:.73rem;color:#827b6d;font-weight:500;}
.ss-note{padding:12px;border:1px solid #cec2ab;border-radius:3px 13px 4px 3px;box-shadow:3px 4px 0 #d2c4ac;margin:11px 0;transform:rotate(-.7deg);color:#554838;}
.ss-note:nth-child(even){transform:rotate(.6deg);}
.ss-note-title{font-size:.81rem;font-weight:800;}.ss-note-body{font-size:.76rem;line-height:1.48;margin-top:6px;white-space:pre-wrap;overflow-wrap:anywhere;}
.ss-tip{background:#eef0e6;border:1px solid #d7decf;border-left:4px solid #819576;padding:12px 13px;border-radius:10px;font-size:.76rem;line-height:1.65;color:#555c4e;}
.ss-footnote{background:#eee8dc;border:1px dashed #cec5b4;border-radius:12px;padding:12px 15px;color:#67665a;font-size:.76rem;}
/* Custom Streamlit elements stay keyboard-friendly and high-contrast. */
@media(max-width:1100px){.ss-header{padding:14px 16px}.ss-right{display:none}.block-container{padding:.5rem .7rem 1.8rem}}
@media(max-width:640px){.ss-icon{width:50px;height:51px;font-size:28px}.ss-brand{gap:12px}.ss-header{min-height:94px}.ss-sub{font-size:.67rem}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{scroll-behavior:auto!important;transition:none!important}}
</style>
""", unsafe_allow_html=True)

# finds the folder where all the project files are saved
BASE = Path(__file__).resolve().parent
# this points to the example pdf that comes with the project
SAMPLE_PDF = BASE / "sample_reading.pdf"
# This custom editor communicates note positions back to Python, unlike a static iframe.
# connects the python code to the interactive pdf editor
pdf_editor = components.declare_component("studyspace_pdf_editor", path=str(BASE / "editor"))

# sets up the information that needs to stay saved while using the website
for name, default in {"doc_hash": "", "page": 1, "notes": [], "highlights": [], "wav": None}.items():
    # only creates a starting value if that information is not already saved
    if name not in st.session_state:
        # stores the starting value so the app can use it later
        st.session_state[name] = default

# caches the pdf information so it does not have to be processed every time
@st.cache_data(show_spinner=False, max_entries=10)
# this function gets the number of pages and the text from the pdf
def cached_info(data: bytes):
    # returns the information from the pdf tools file
    return pdf_info(data)

# caches each page so opening the same page is faster
@st.cache_data(show_spinner=False, max_entries=16)
# gets the visible pdf page and the text positions used for reading
def cached_page(data: bytes, index: int):
    # returns the page image and reading information
    return page_visual_and_segments(data, index)

# keeps a saved version of the pdf preview for repeated use
@st.cache_data(show_spinner=False, max_entries=12)
# this function prepares a pdf preview with the saved highlights
def preview_pdf(data: bytes, highlights_json: str):
    # Sticky notes appear as draggable HTML over the PDF while editing,
    # so the preview only needs permanent highlights, not flattened notes.
    # adds highlights to the preview without saving the sticky notes onto it yet
    return annotated_pdf(data, json.loads(highlights_json), [])

# caches the finished file so it does not need to be rebuilt unnecessarily
@st.cache_data(show_spinner=False, max_entries=12)
# this function creates the final pdf with the notes and highlights
def export_pdf(data: bytes, highlights_json: str, notes_json: str):
    # returns the finished pdf that the user can download
    return annotated_pdf(data, json.loads(highlights_json), json.loads(notes_json))

# 4a) edit after 1st draft
# add a button that checks whether the computer speech engine is working
# The live browser has a Try voice button and voice selection instead.
# this function creates a wav audio file from the pdf text
def generate_wav(text: str, speech_rate: int = 160, volume: float = 1.0):
    import pyttsx3  # text-to-speech conversion library
    # creates a temp file where the audio will be stored
    # makes a temporary wav file to hold the speech audio
    audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    # gets the location of that temporary file
    audio_path = audio_file.name  # saves the temporary file's path
    # closes the temporary file before the speech engine saves audio to it
    audio_file.close()  # closes the file before pyttsx3 writes to it
    # uses try so the temporary audio file can still be cleaned up afterward
    try:
        # starts the computer speech engine
        engine = pyttsx3.init()  # starts the text-to-speech engine
        # changes how fast the voice reads the text
        engine.setProperty("rate", speech_rate)  # applies the selected reading speed
        # sets how loud the voice will be
        engine.setProperty("volume", volume)  # selected volume
        # tells the engine to save the reading as an audio file
        engine.save_to_file(text, audio_path)  # saves the typed text as audio
        # finishes creating the audio file
        engine.runAndWait()  # run speech engine
        # stops the speech engine after the audio is made
        engine.stop()  # stop the speech engine
        # checks whether the audio file was created successfully
        # makes sure the audio file actually has content in it
        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 44:
            # opens the audio file so it can be read by the app
            with open(audio_path, "rb") as audio:  # opens the audio file
                # returns the audio information for playback or downloading
                return audio.read()  # reads the audio data
        # shows an error if the audio file was not created correctly
        raise RuntimeError("The audio file was not created.")
    # this runs at the end even if something went wrong
    finally:
        # deletes the temporary audio file
        # checks whether the temporary audio file is still there
        if os.path.exists(audio_path):
            # removes the temporary file since it is no longer needed
            os.remove(audio_path)

# this section creates the main studyspace heading at the top
# ------------ Branded reading desk ------------
# adds the notebook design, app name, and short description
st.markdown('''<div class="ss-header"><div class="ss-brand">
  <div class="ss-icon" aria-hidden="true">📓</div>
  <div><div class="ss-eyebrow">Your quiet study corner</div>
  <div class="ss-name">study<b>space.</b></div>
  <div class="ss-sub">Good books. Better focus. A little room to think.</div></div>
  </div><div class="ss-right"><span class="ss-index">FIELD NOTES / 01</span>
  <span class="ss-tag accent">✿ read + follow</span><span class="ss-tag">◫ movable notes</span>
  <span class="ss-tag">✎ gentle highlights</span></div></div>''', unsafe_allow_html=True)

# adds a section where students can upload a pdf
with st.expander("📎  Your documents  ·  upload or switch a PDF", expanded=False):
    # lets the user choose a pdf from their computer
    uploaded = st.file_uploader("Upload a PDF", type=["pdf"], help="Best for text-based PDFs. Scanned PDFs need OCR.")
    # explains how to try the sample file and keep any notes they make
    st.caption("You can practice using the sample PDF if you haven't uploaded one yet. Download your annotated PDF to keep notes permanently.")

# uses the uploaded pdf or the sample pdf if nothing was uploaded
pdf_bytes = uploaded.getvalue() if uploaded else SAMPLE_PDF.read_bytes()
# shows the file name for whichever document is being used
filename = uploaded.name if uploaded else "Sample reading — the science of learning.pdf"
# tries to open the pdf and get its text and page information
try:
    # gets the page count and text for the uploaded document
    pages, page_texts = cached_info(pdf_bytes)
# this catches an error if the pdf cannot be opened
except Exception as error:
    # shows the error on the website instead of hiding it
    st.error(f"Could not load this PDF: {error}")
    # stops the app from continuing with an invalid pdf
    st.stop()

# creates a unique code for the pdf so different documents do not share notes
pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()
# checks whether the user opened a different document
if st.session_state.doc_hash != pdf_hash:
    # saves the unique code for the current document
    st.session_state.doc_hash = pdf_hash
    # starts the new document on the first page
    st.session_state.page = 1
    # clears sticky notes from the previous document
    st.session_state.notes = []
    # clears highlights from the previous document
    st.session_state.highlights = []
    # clears the previous audio recording
    st.session_state.wav = None

# makes sure the page number stays within the available pdf pages
page_no = min(pages, max(1, st.session_state.page))
# changes the displayed page number to the index used by python
page_index = page_no - 1
# converts the current highlights to json for the pdf preview
hjson = json.dumps(st.session_state.highlights, sort_keys=True)
# creates a preview that includes any highlights already made
preview_bytes = preview_pdf(pdf_bytes, hjson)

# shows which pdf is open and how many notes and highlights it has
st.markdown(f'''<div class="ss-file"><div><div class="ss-docname">📄 &nbsp;{html.escape(filename)}</div>
<div class="ss-detail">{pages} pages · {sum(len(p.split()) for p in page_texts):,} words · {len(st.session_state.highlights)} highlights · {len(st.session_state.notes)} sticky notes</div></div>
<div class="ss-tag accent">● &nbsp;IN YOUR READING NOOK</div></div>''', unsafe_allow_html=True)

# these controls let students move around the pdf pages
# ------------ Navigation and wide PDF ------------
# splits the navigation tools into columns across the screen
prev, next_, choose, focus_col = st.columns([1.1, 1.1, 2.2, 1.6], vertical_alignment="bottom")
# this column has the button to go back one page
with prev:
    # checks if the previous page button was clicked
    if st.button("← Previous", disabled=page_no <= 1, use_container_width=True):
        # moves the document back one page
        st.session_state.page = page_no - 1
        # refreshes the website to show that page
        st.rerun()
# this column has the button for going to the next page
with next_:
    # checks if the next page button was clicked
    if st.button("Next →", disabled=page_no >= pages, use_container_width=True):
        # moves the document forward one page
        st.session_state.page = page_no + 1
        # refreshes the website to show the next page
        st.rerun()
# this lets the user choose a page directly
with choose:
    # creates the dropdown with all the available pdf pages
    choice = st.selectbox("PDF page", range(1, pages+1), index=page_index, format_func=lambda n:f"Page {n} of {pages}", label_visibility="collapsed")
    # checks whether a different page was selected
    if choice != page_no:
        # saves the page the user chose
        st.session_state.page = choice
        # reloads the app to display the chosen page
        st.rerun()
# this controls the option for making the pdf full width
with focus_col:
    # adds a switch so the user can focus on just the document
    focus = st.toggle("Full-width paper", value=False, help="Expand PDF editor and hide the study toolbox.")

# checks if the full width reading option is turned on
if focus:
    # creates a bigger space for the document
    workspace = st.container()
    # hides the note and highlight panel in this view
    inspector = None
# uses the regular layout when full width is turned off
else:
    # puts the pdf and the study tools next to each other
    workspace, inspector = st.columns([7.6, 2.4], gap="medium")

# this is the main area where the pdf is displayed
with workspace:
    # adds a title above the reading area
    st.markdown('<div class="ss-section">The reading desk <span class="ss-muted">· a page for everything on your mind</span></div>', unsafe_allow_html=True)
    # gets the selected pdf page ready to display
    page_data = cached_page(preview_bytes, page_index)
    # finds only the sticky notes that belong on this page
    notes_on_page = [n for n in st.session_state.notes if n.get('page') == page_index]
    # opens the interactive pdf editor and gives it the current information
    result = pdf_editor(
        # passes in the current page and its reading information
        page_data=page_data,
        # passes in the sticky notes for the page
        notes=notes_on_page,
        # tells the editor which page number is open
        page=page_index,
        # connects the editor to the correct pdf document
        doc_hash=pdf_hash,
        # gives the editor a consistent name so streamlit can keep track of it
        key="studyspace_editor",
        # allows the editor to start without returning any changes
        default=None,
    )
    # the editor sends note updates after a user types or moves a note
    # The editor returns note positions on each completed drag or note edit.
    # Only accept updates for the currently open PDF and page.
    # makes sure the note update matches the pdf and page being viewed
    if isinstance(result, dict) and result.get('event') == 'notes' and result.get('doc_hash') == pdf_hash and result.get('page') == page_index:
        # creates a new list to collect notes returned from the editor
        new_notes = []
        # looks through the saved notes from the editor and limits how many it reads
        for note in (result.get('notes') or [])[:100]:
            # checks that each note has the expected information format
            if not isinstance(note, dict):
                # skips anything that is not a proper note
                continue
            # tries to read the location of the sticky note on the page
            try:
                # keeps the note within the horizontal space of the pdf
                x = min(76., max(0., float(note.get('x', 0))))
                # keeps the note within the vertical space of the pdf
                y = min(90., max(0., float(note.get('y', 0))))
            # catches a problem if the note position is not a valid number
            except (ValueError, TypeError):
                # skips the note if its position cannot be used
                continue
            # adds the note details to the list of updated notes
            new_notes.append({
                # keeps the note id and the pdf page it belongs to
                "id": str(note.get("id", ""))[:90], "page": page_index,
                # saves the title while limiting how long it can be
                "title": str(note.get("title", "Study note"))[:70],
                # saves the note text while limiting how much is included
                "body": str(note.get("body", ""))[:1000],
                # only accepts colors that the project already supports
                "color": note.get("color") if note.get("color") in NOTE_COLORS else "Butter",
                # rounds the location values so the note stays in the right spot
                "x": round(x, 2), "y": round(y, 2),
            })
        # keeps notes from the other pages and updates the current page notes
        updated = [n for n in st.session_state.notes if n.get('page') != page_index] + new_notes
        # checks whether anything about the notes actually changed
        if updated != st.session_state.notes:
            # saves the new notes into the app session
            st.session_state.notes = updated
    # adds a way to view and copy the pdf text separately
    with st.expander("♿ Accessible extracted text (select and copy)"):
        # shows the text extracted from this page in a read-only box
        st.text_area("Text from this PDF page", page_texts[page_index], height=220, disabled=True)

# checks whether the regular study tools panel is visible
if inspector is not None:
    # opens the panel beside the document
    with inspector:
        # adds the heading for the notes and study tools area
        st.markdown('<div class="ss-section">Your desk drawer</div>', unsafe_allow_html=True)
        # makes separate tabs for sticky notes, highlighting, and audio
        tab_notes, tab_mark, tab_audio = st.tabs(["Notes", "Highlight", "Audio"])
        # this part shows the sticky notes the student has made
        with tab_notes:
            # explains how to place, move, and delete a sticky note
            st.markdown('<div class="ss-tip">Choose <b>Place note</b> above the paper, click to stick it down, and type your thought. Drag the top edge to move it, or use × to remove it.</div>', unsafe_allow_html=True)
            # gets the saved notes for the current page
            notes_on_page = [n for n in st.session_state.notes if n.get('page') == page_index]
            # shows how many sticky notes are on that page
            st.caption(f"{len(notes_on_page)} notes on this page")
            # goes through each note so it can appear in the notes panel
            for item in notes_on_page:
                # gets the color chosen for the sticky note
                fill = NOTE_COLORS.get(item['color'], NOTE_COLORS['Butter'])
                # converts the note color into rgb values
                rgb = tuple(round(v*255) for v in fill)
                # turns the rgb values into a color the website can display
                color = '#%02x%02x%02x' % rgb
                # displays the note title and its text using the selected color
                st.markdown(f'''<div class="ss-note" style="background:{color}"><div class="ss-note-title">{html.escape(item['title'])}</div>
                <div class="ss-note-body">{html.escape(item['body']) or '<em>Click the note on paper to type…</em>'}</div></div>''',unsafe_allow_html=True)
        # this tab lets the user highlight important phrases
        with tab_mark:
            # creates the form for typing what should be highlighted
            with st.form("highlight", clear_on_submit=True):
                # lets the user enter a word or phrase they want to mark
                phrase = st.text_input("Find phrase", placeholder="e.g. active recall")
                # lets the user choose one of the highlighter colors
                color = st.selectbox("Highlighter", list(PALETTE))
                # adds the option to highlight the phrase throughout the whole pdf
                all_pages = st.checkbox("Mark every page", value=False)
                # creates the button that adds a highlight
                go = st.form_submit_button("Add highlight", type="primary", use_container_width=True)
            # checks whether the highlight button was clicked
            if go:
                # removes extra spaces from the phrase before searching
                phrase = phrase.strip()
                # searches the current page or every page for matching text
                matches = count_matches(pdf_bytes, phrase, list(range(pages)) if all_pages else [page_index]) if phrase else {}
                # checks if the phrase was found in the document
                if sum(matches.values()) == 0:
                    # shows a message if there were no matching words
                    st.warning("No matching text. Try a shorter phrase.")
                # continues if there are matching phrases
                else:
                    # goes through the pages where the phrase was found
                    for index, count in matches.items():
                        # checks if that page has at least one match
                        if count:
                            # saves the highlight with its page, phrase, and color
                            st.session_state.highlights.append({"page":index,"phrase":phrase,"color":color})
                    # reloads the page so the new highlight appears
                    st.rerun()
            # lists the highlights that have been saved
            for index, h in enumerate(st.session_state.highlights):
                # only shows highlights for the page currently open
                if h['page']==page_index:
                    # displays the highlight color and marked phrase
                    st.caption(f"{h['color']} · {h['phrase']}")
                    # adds a button to remove that highlight
                    if st.button("Remove", key=f"rmhi_{index}",use_container_width=True):
                        # deletes the selected highlight from the list
                        del st.session_state.highlights[index]
                        # updates the page after removing the highlight
                        st.rerun()
        # this tab gives information and options for listening to the pdf
        with tab_audio:
            # explains how to choose and try a reading voice
            st.markdown('<div class="ss-tip">Choose a voice in the bar <b>above the PDF</b>, click <b>Preview voice</b>, then <b>Read + follow</b>. More natural voices appear when available on your device.</div>', unsafe_allow_html=True)
            # reminds the user that voice options depend on their browser and computer
            st.caption("Browser voices vary across Windows, Chrome and Edge. For better quality, try Microsoft natural voices if they appear in the voice menu.")
            # opens the optional section for saving the spoken text as a wav file
            with st.expander("Download page audio as WAV"):
                # explains that the downloaded audio uses the computer speech engine
                st.caption("This optional WAV uses your computer's pyttsx3 voice, not the browser voice selected above.")
                # allows the user to set the reading speed for the wav recording
                speed = st.slider("Reading Speed (words per minute):",100,300,160,10)
                # allows the user to change the wav recording volume
                volume = st.slider("Volume:",0.,1.,1.,.1)
                # 5) create a button that allows the user to start the reading
                # checks if the user wants to create an audio file
                if st.button("Generate WAV",use_container_width=True):
                    # checks if the text area is empty
                    # makes sure the pdf page has text that can be read
                    if not page_texts[page_index].strip():
                        # shows a warning if there is no readable text on this page
                        st.warning("Please upload a text-based PDF to read.")
                    # continues if the pdf contains readable text
                    else:
                        # tries to generate the audio from this page
                        try:
                            # stores the created audio in the current app session
                            st.session_state.wav = generate_wav(page_texts[page_index], speed, volume)
                        # catches an error if the audio could not be created
                        except Exception as error:
                            # shows what went wrong with the speech generation
                            st.error(f"Speech generation failed: {error}")
                # checks if a saved audio recording is available
                if st.session_state.wav:
                    # displays the audio player
                    # shows the audio player so the recording can be played
                    st.audio(st.session_state.wav,format="audio/wav")
                    # creates a download button
                    # creates the button to download the recording
                    st.download_button("Download Audio",st.session_state.wav,file_name="generated_speech.wav",mime="audio/wav")

# this last section lets the user keep the pdf with their notes and highlights
# Save button appears AFTER processing editor notes, so newly placed/moved
# sticky notes are included in the PDF download without another click.
# adds a heading above the pdf download button
st.markdown('<div class="ss-section">Keep your field notes</div>',unsafe_allow_html=True)
# creates the finished pdf using the current saved notes and highlights
saved = export_pdf(pdf_bytes,json.dumps(st.session_state.highlights,sort_keys=True),json.dumps(st.session_state.notes,sort_keys=True))
# adds a download button with the original file name and studyspace added
st.download_button("↓ Save annotated PDF",saved,file_name=f"{Path(filename).stem}_studyspace.pdf",mime="application/pdf",type="primary")
# reminds students to save the pdf before closing their study session
st.markdown('<div class="ss-footnote">☕ Your marks and sticky notes stay in this open session. Save an annotated copy before you close StudySpace. The notes will appear directly on your PDF.</div>', unsafe_allow_html=True)
