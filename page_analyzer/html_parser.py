from bs4 import BeautifulSoup


def limit_length(text, max_length=255):
    if text is not None:
        return text[:max_length]
    return text


def parse_html(html_markup):
    soup = BeautifulSoup(html_markup, 'html.parser')

    h1_tag = soup.find('h1')
    h1 = h1_tag.text.strip() if h1_tag else None

    title_tag = soup.find('title')
    title = title_tag.text.strip() if title_tag else None

    meta = soup.find('meta', attrs={'name': 'description'})
    if meta and 'content' in meta.attrs:
        description = meta.get('content').strip()
    else:
        description = None

    return {
        'title': limit_length(title),
        'description': description,
        'h1': limit_length(h1)
    }
