import json

import streamlit as st
import streamlit.components.v1 as components

from i18n import LANGUAGES, language_display_name, translate
from ui.state import get_current_language


_SPEECH_LOCALES = {
    "en": "en-US", "es": "es-ES", "pt": "pt-PT", "fr": "fr-FR",
    "de": "de-DE", "it": "it-IT", "ru": "ru-RU", "sv": "sv-SE",
    "fi": "fi-FI", "pl": "pl-PL", "zh": "zh-CN", "ja": "ja-JP",
    "ko": "ko-KR",
}


def _to_safe_js_string(value: object) -> str:
    literal = json.dumps(str(value), ensure_ascii=False)
    return (
        literal.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def render_voice_prompt():
    language = get_current_language()
    speak = st.button(f"🎙 {translate('voice.prompt', language)}", use_container_width=True)

    if speak:
        script = """
<script>
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
    const recognition = new SpeechRecognition();
    recognition.lang = __SPEECH_LANGUAGE__;
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = function(event) {
        const text = event.results[0][0].transcript;
        const streamlitDoc = window.parent.document;
        const textarea = streamlitDoc.querySelector('textarea');

        if (textarea) {
            textarea.value = text;
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
        }
    };

    recognition.start();
}
</script>
""".replace(
            "__SPEECH_LANGUAGE__",
            _to_safe_js_string(_SPEECH_LOCALES[language]),
        )
        components.html(
            script,
            height=0,
        )


def _speak(text, lang):
    text_literal = _to_safe_js_string(text)
    lang_literal = _to_safe_js_string(lang)

    components.html(
        f"""
<script>
const text = {text_literal};
const utterance = new SpeechSynthesisUtterance(text);
utterance.rate = 1.0;
utterance.pitch = 1.0;
utterance.lang = {lang_literal};
window.speechSynthesis.cancel();
window.speechSynthesis.speak(utterance);
</script>
""",
        height=0,
    )


def render_voice_assistant(concept_data):
    language = get_current_language()
    st.markdown(f"## 🧠 {translate('voice.assistant', language)}")

    title = concept_data.get("title", "")
    executive_summary = concept_data.get("executive_summary", "")
    market_demand = concept_data.get("market_demand", "")
    investor_summary = concept_data.get("investor_summary", "")
    modern_principle = concept_data.get("modern_principle", "")

    voice_language_key = "voice_language_selector"
    legacy_voice_languages = {"English": "en", "Русский": "ru"}
    stored_voice_language = st.session_state.get(voice_language_key, language)
    stored_voice_language = legacy_voice_languages.get(stored_voice_language, stored_voice_language)
    if stored_voice_language not in LANGUAGES:
        stored_voice_language = language
    st.session_state[voice_language_key] = stored_voice_language

    voice_language = st.selectbox(
        translate("voice.language", language),
        list(LANGUAGES),
        key=voice_language_key,
        format_func=language_display_name,
    )

    summary_text = translate("voice.summary_text", voice_language, title=title, summary=executive_summary, market=market_demand, investor=investor_summary)
    investor_text = translate("voice.investor_text", voice_language, title=title, investor=investor_summary, market=market_demand)
    engineering_text = translate("voice.engineering_text", voice_language, title=title, principle=modern_principle)
    speech_lang = _SPEECH_LOCALES[voice_language]

    top1, top2, top3 = st.columns(3)
    with top1:
        play_summary = st.button(f"▶ {translate('voice.summary', language)}", key="voice_summary", use_container_width=True)
    with top2:
        play_investor = st.button(f"🎧 {translate('voice.investor', language)}", key="voice_investor", use_container_width=True)
    with top3:
        play_engineering = st.button(f"⚙ {translate('voice.engineering', language)}", key="voice_engineering", use_container_width=True)

    bottom1, bottom2, bottom3 = st.columns(3)
    with bottom1:
        pause_voice = st.button(f"⏸ {translate('voice.pause', language)}", key="voice_pause", use_container_width=True)
    with bottom2:
        resume_voice = st.button(f"▶ {translate('voice.resume', language)}", key="voice_resume", use_container_width=True)
    with bottom3:
        stop_voice = st.button(f"⏹ {translate('voice.stop', language)}", key="voice_stop", use_container_width=True)


    if play_summary:
        _speak(summary_text, speech_lang)
    if play_investor:
        _speak(investor_text, speech_lang)
    if play_engineering:
        _speak(engineering_text, speech_lang)
    if pause_voice:
        components.html("<script>window.speechSynthesis.pause();</script>", height=0)
    if resume_voice:
        components.html("<script>window.speechSynthesis.resume();</script>", height=0)
    if stop_voice:
        components.html("<script>window.speechSynthesis.cancel();</script>", height=0)
