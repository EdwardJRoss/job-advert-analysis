import re
from html2text import HTML2Text
from bs4 import BeautifulSoup
import mistletoe

def html2md(html):
    parser = HTML2Text()
    parser.ignore_images = True
    parser.ignore_anchors = True
    parser.body_width = 0
    md = parser.handle(html)
    return md

def html2plain(html):
    # HTML to Markdown
    md = html2md(html)
    # Normalise custom lists
    md = re.sub(r'(^|\n) ? ? ?\\?[·--*]( \w)', r'\1  *\2', md)
    # Convert back into HTML
    html_simple = mistletoe.markdown(md)
    # Convert to plain text
    soup = BeautifulSoup(html_simple)
    text = soup.getText()
    # Strip off table formatting
    text = re.sub(r'(^|\n)\|\s*', r'\1', text)
    # Strip off extra emphasis
    text = re.sub(r'\*\*', '', text)
    # Remove trailing whitespace and leading newlines
    text = re.sub(r' *$', '', text)
    text = re.sub(r'\n\n+', r'\n\n', text)
    text = re.sub(r'^\n+', '', text)
    return text
