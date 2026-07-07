import os
import re
import imaplib
import email
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def load_env_file():
    if not os.path.exists(".env"):
        return

    with open(".env") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    load_env_file()

username = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

UNSUBSCRIBE_WORDS = [
    "unsubscribe",
    "opt out",
    "opt-out",
    "remove me",
    "manage preferences",
    "email preferences",
    "subscription preferences",
]


def connect_to_email():
    if not username or not password:
        missing = []

        if not username:
            missing.append("EMAIL")

        if not password:
            missing.append("PASSWORD")

        raise RuntimeError("Missing " + ", ".join(missing) + " in your .env file")

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    mail.select("inbox")
    return mail


def looks_like_unsubscribe(text):
    text = " ".join(text.lower().split())
    return any(word in text for word in UNSUBSCRIBE_WORDS)


def get_header_unsubscribe_links(msg):
    links = []
    header = msg.get("List-Unsubscribe")

    if not header:
        return links

    # Header links usually look like: <https://...>, <mailto:...>
    links.extend(re.findall(r"<([^>]+)>", header))

    return links


def get_links_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    links = []

    for link in soup.find_all("a", href=True):
        href = link["href"].strip()
        visible_text = link.get_text(" ", strip=True)
        title = link.get("title", "")
        aria_label = link.get("aria-label", "")

        combined_text = " ".join([href, visible_text, title, aria_label])

        if looks_like_unsubscribe(combined_text):
            links.append(href)

    return links


def get_links_from_text(text_content):
    links = []

    for match in re.finditer(r"https?://\S+", text_content):
        url = match.group(0).rstrip(").,;]")
        nearby_text = text_content[max(0, match.start() - 100):match.end() + 100]

        if looks_like_unsubscribe(nearby_text):
            links.append(url)

    return links


def click_link(link):
    if link.startswith("mailto:"):
        print("Manual mail unsubscribe needed:", link)
        return

    try:
        response = requests.get(link, timeout=20, allow_redirects=True)

        if response.status_code == 200:
            print("Successfully visited:", link)
        else:
            print("Failed to visit:", link, "Error Code:", response.status_code)

    except Exception as e:
        print("Failed to visit:", link, str(e))


def search_inbox():
    mail = connect_to_email()

    date_cutoff = (datetime.now() - timedelta(days=15)).strftime("%d-%b-%Y")
    _, search_data = mail.search(None, f'(SINCE {date_cutoff})')
    data = search_data[0].split()

    links = []

    for num in data:
        _, fetch_data = mail.fetch(num, "(RFC822)")
        msg = email.message_from_bytes(fetch_data[0][1])

        links.extend(get_header_unsubscribe_links(msg))

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()

                if part.get_content_disposition() == "attachment":
                    continue

                payload = part.get_payload(decode=True)
                if not payload:
                    continue

                content = payload.decode(errors="ignore")

                if content_type == "text/html":
                    links.extend(get_links_from_html(content))
                elif content_type == "text/plain":
                    links.extend(get_links_from_text(content))
        else:
            content_type = msg.get_content_type()
            payload = msg.get_payload(decode=True)

            if not payload:
                continue

            content = payload.decode(errors="ignore")

            if content_type == "text/html":
                links.extend(get_links_from_html(content))
            elif content_type == "text/plain":
                links.extend(get_links_from_text(content))

    mail.logout()
    return list(dict.fromkeys(links))


def save_links(links):
    with open("links.txt", "w") as f:
        f.write("\n".join(links))


def main():
    links = search_inbox()

    for link in links:
        click_link(link)

    save_links(links)


if __name__ == "__main__":
    main()
