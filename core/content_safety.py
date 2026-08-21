import re
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlparse


ALLOWED_TAGS = {
    "a", "b", "blockquote", "br", "div", "em", "figcaption", "figure", "h2", "h3",
    "i", "img", "li", "ol", "p", "s", "strong", "u", "ul",
}
VOID_TAGS = {"br", "img"}
ALLOWED_ATTRIBUTES = {
    "a": {"href", "target", "rel", "title"},
    "img": {"src", "alt", "title"},
}
TAG_PATTERN = re.compile(r"<[a-zA-Z][^>]*>")


def _safe_url(value, *, image=False):
    parsed = urlparse(value)
    if parsed.scheme in {"javascript", "data", "vbscript", "file"}:
        return ""
    if image:
        if value.startswith("/media/"):
            return value
        return value if parsed.scheme in {"http", "https"} and parsed.netloc else ""
    if value.startswith(("/", "#", "?")):
        return value
    return value if parsed.scheme in {"http", "https", "mailto"} and (parsed.netloc or parsed.scheme == "mailto") else ""


class _NewsHTMLSanitizer(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.output = []
        self.open_tags = []
        self.ignored_tags = []

    def handle_data(self, data):
        if self.ignored_tags:
            return
        self.output.append(escape(data))

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in {"iframe", "object", "script", "style"}:
            self.ignored_tags.append(tag)
            return
        if self.ignored_tags:
            return
        if tag not in ALLOWED_TAGS:
            return

        clean_attrs = []
        for name, value in attrs:
            name = name.lower()
            if name not in ALLOWED_ATTRIBUTES.get(tag, set()) or value is None:
                continue
            if name in {"href", "src"}:
                value = _safe_url(value, image=tag == "img")
                if not value:
                    continue
            clean_attrs.append(f' {name}="{escape(value, quote=True)}"')

        self.output.append(f"<{tag}{''.join(clean_attrs)}>")
        if tag not in VOID_TAGS:
            self.open_tags.append(tag)

    def handle_startendtag(self, tag, attrs):
        if self.ignored_tags:
            return
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if self.ignored_tags:
            if self.ignored_tags[-1] == tag:
                self.ignored_tags.pop()
            return
        if tag not in self.open_tags:
            return
        while self.open_tags:
            current = self.open_tags.pop()
            self.output.append(f"</{current}>")
            if current == tag:
                break

    def result(self):
        while self.open_tags:
            self.output.append(f"</{self.open_tags.pop()}>")
        return "".join(self.output)


def _plain_text_to_html(value):
    value = value.strip()
    if not value:
        return ""
    paragraphs = re.split(r"\n\s*\n", value)
    return "".join(
        f"<p>{escape(paragraph).replace(chr(10), '<br>')}</p>"
        for paragraph in paragraphs
    )


def sanitize_news_content(value):
    value = value or ""
    if not TAG_PATTERN.search(value):
        return _plain_text_to_html(value)
    parser = _NewsHTMLSanitizer()
    parser.feed(value)
    parser.close()
    return parser.result()
