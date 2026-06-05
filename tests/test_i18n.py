from command_book.i18n import _, _detect_lang


def test_detect_lang_cb_lang(monkeypatch):
    monkeypatch.setenv("CB_LANG", "en")
    assert _detect_lang() == "en"


def test_detect_lang_cb_lang_es(monkeypatch):
    monkeypatch.setenv("CB_LANG", "es")
    assert _detect_lang() == "es"


def test_detect_lang_from_lang_env(monkeypatch):
    monkeypatch.delenv("CB_LANG", raising=False)
    monkeypatch.setenv("LANG", "en_US.UTF-8")
    assert _detect_lang() == "en"


def test_detect_lang_fallback_to_en(monkeypatch):
    monkeypatch.delenv("CB_LANG", raising=False)
    monkeypatch.setenv("LANG", "zh_CN.UTF-8")  # unsupported language
    assert _detect_lang() == "en"


def test_translate_returns_string():
    result = _("app_help")
    assert isinstance(result, str)
    assert len(result) > 0


def test_translate_unknown_key_returns_key():
    assert _("nonexistent_key_xyz") == "nonexistent_key_xyz"
