SUPPORTED_LANGS = ("ko", "en", "jp", "cn")
DEFAULT_LANG = "ko"


def localize(jsonb_field: dict | None, lang: str) -> str:
    if not jsonb_field:
        return ""
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG
    return jsonb_field.get(lang) or jsonb_field.get(DEFAULT_LANG, "")
