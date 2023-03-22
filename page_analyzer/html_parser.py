from bs4 import BeautifulSoup


def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    h1_tag = soup.find('h1')
    h1 = h1_tag.text.strip() if h1_tag else None

    title_tag = soup.find('title')
    title = title_tag.text.strip() if title_tag else None

    meta = soup.find('meta', attrs={'name': 'description'})
    description = meta['content'].strip() if meta else None

    return {
        'title': title,
        'description': description,
        'h1': h1
    }
