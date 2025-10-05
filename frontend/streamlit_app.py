import httpx
import streamlit as st
import time
from typing import List, Dict, Any, Optional

# ---------------- CLIENT ----------------
class AutocompleteClient:
    def __init__(self, base_url: str, timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def autocomplete(
        self,
        text: str,
        max_predictions: int = 5,
        categories: Optional[List[str]] = None,
        output_language: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "input": text,
            "max_predictions": max_predictions,
            "categories": categories,
            "output_language": output_language,
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(f"{self.base_url}/api/v1/autocomplete", json=payload)
            resp.raise_for_status()
            return resp.json()

# ---------------- DEBOUNCER ----------------
class Debouncer:
    def __init__(self, interval_seconds: float = 0.25):
        self.interval = interval_seconds
        self._last_time: float = 0.0

    def ready(self) -> bool:
        now = time.time()
        if now - self._last_time >= self.interval:
            self._last_time = now
            return True
        return False

# ---------------- STREAMLIT CONFIG ----------------
st.set_page_config(page_title="Legal Autocomplete (Real-Time)", page_icon="⚖️")

# ---------------- SESSION STATE ----------------
if "query" not in st.session_state:
    st.session_state.query = "contract"
if "suggestions" not in st.session_state:
    st.session_state.suggestions = []
if "error" not in st.session_state:
    st.session_state.error = None
if "last_fetched_query" not in st.session_state:
    st.session_state.last_fetched_query = ""
if "debouncer" not in st.session_state:
    st.session_state.debouncer = Debouncer(0.3)

# ---------------- SIDEBAR ----------------
st.sidebar.title("Settings")

backend_url = st.sidebar.text_input("Backend URL", "http://localhost:8000")
max_predictions = st.sidebar.slider("Max Predictions", 1, 20, 5)
language = st.sidebar.selectbox("Output Language", ["en", "de", "fr", "es", "it"])
categories_input = st.sidebar.text_input("Categories", "Contract Law, Consumer Rights")
min_chars = st.sidebar.number_input("Min chars before querying", 1, 10, 2)
highlight_suffix = st.sidebar.checkbox("Highlight completion suffix", True)
show_category = st.sidebar.checkbox("Show category labels", True)

# ---------------- CLIENT ----------------
client = AutocompleteClient(backend_url, timeout=5.0)

# ---------------- CSS ----------------
st.markdown("""
<style>
.autocomplete-container {
    margin-top: 0.75rem;
    border: 1px solid #2b2b2b22;
    border-radius: 8px;
    padding: 0.4rem 0.6rem 0.2rem 0.6rem;
    background: #fafafa;
}
.suggestion-item {
    padding: 0.35rem 0.4rem;
    border-radius: 4px;
    cursor: pointer;
    margin-bottom: 0.15rem;
    line-height: 1.25;
    display: flex;
    justify-content: space-between;
    align-items: baseline;
}
.suggestion-item:hover {
    background: #e8f2ff;
}
.suggestion-text {
    font-size: 0.92rem;
    font-family: "Segoe UI", system-ui, sans-serif;
    color: #222;
    flex: 1 1 auto;
}
.suggestion-cat {
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    opacity: 0.55;
    letter-spacing: 0.5px;
    white-space: nowrap;
}
.suggestion-highlight {
    font-weight: 600;
    color: #0b63c7;
}
.no-suggestions {
    font-size: 0.8rem;
    opacity: 0.6;
    padding: 0.4rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HELPERS ----------------
def parse_categories(raw: str):
    cats = [c.strip() for c in raw.split(",") if c.strip()]
    return cats or None

def format_suggestion(user_input: str, suggestion_text: str) -> str:
    if not highlight_suffix:
        return suggestion_text
    lower_in, lower_sug = user_input.lower(), suggestion_text.lower()
    if lower_sug.startswith(lower_in):
        suffix = suggestion_text[len(user_input):]
        return f"{user_input}<span class='suggestion-highlight'>{suffix}</span>"
    return suggestion_text

def fetch_suggestions_if_needed():
    q = st.session_state.query.strip()
    if len(q) < min_chars:
        st.session_state.suggestions = []
        return
    if q == st.session_state.last_fetched_query:
        return
    if not st.session_state.debouncer.ready():
        return
    try:
        resp = client.autocomplete(
            text=q,
            max_predictions=max_predictions,
            categories=parse_categories(categories_input),
            output_language=language,
        )
        if resp.get("success", True):
            st.session_state.suggestions = resp.get("data", {}).get("suggestions", [])
            st.session_state.error = None
        else:
            st.session_state.error = resp.get("message", "Unknown error")
            st.session_state.suggestions = []
        st.session_state.last_fetched_query = q
    except Exception as e:
        st.session_state.error = str(e)
        st.session_state.suggestions = []

def adopt_suggestion(text: str):
    st.session_state.query = text
    st.session_state.last_fetched_query = ""
    fetch_suggestions_if_needed()

# ---------------- UI ----------------
st.title("⚖️ Real-Time Legal Autocomplete")
st.caption("Start typing below — suggestions appear instantly like Google search.")

# Automatically call backend as user types
st.text_input(
    "Type a legal phrase:",
    key="query",
    placeholder="e.g. contract termination notice...",
    on_change=fetch_suggestions_if_needed,  # <- triggers real-time fetch
)

# Trigger fetch every run (useful when text_input reruns app)
fetch_suggestions_if_needed()

# ---------------- DISPLAY ----------------
if st.session_state.error:
    st.warning(f"Backend error: {st.session_state.error}")

st.markdown("<div class='autocomplete-container'>", unsafe_allow_html=True)
if st.session_state.suggestions:
    for idx, sug in enumerate(st.session_state.suggestions):
        sug_text = sug.get("text", "")
        sug_cat = sug.get("category") or "General"
        formatted = format_suggestion(st.session_state.query, sug_text)
        # Render clickable suggestion
        if st.button(sug_text, key=f"s_{idx}", use_container_width=True):
            adopt_suggestion(sug_text)
        st.markdown(
            f"<div class='suggestion-item'><div class='suggestion-text'>{formatted}</div>"
            f"{f'<div class=\"suggestion-cat\">{sug_cat}</div>' if show_category else ''}</div>",
            unsafe_allow_html=True,
        )
else:
    st.markdown("<div class='no-suggestions'>No suggestions yet. Keep typing...</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
