import os
import imaplib
import email
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

username = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

def connect_to_email():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    mail.select("inbox")
    return mail

def get_links_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    links = []

    for link in soup.find_all("a", href=True):
        url = link["href"].lower()
        visible_text = link.get_text().lower()

        if "unsubscribe" in url or "unsubscribe" in visible_text:
            links.append(link["href"])

    return links

def click_link(link):
    try:
        response = requests.get(link)
        if response.status_code == 200:
            print("Successfully Visited ", link)

        else:
            print("Failed to visit ", link, "Error Code: ", response.status_code)

    except Exception as e:
        print("Failed to visit ", link, str(e))

def search_inbox():
    mail = connect_to_email()

    date_cutoff = (datetime.now() - timedelta(days=15)).strftime("%d-%b-%Y")
    _, search_data = mail.search(None, f'(SINCE {date_cutoff} BODY "unsubscribe")')
    data = search_data[0].split()

    links = []

    for num in data:
        _, fetch_data = mail.fetch(num, '(RFC822)')
        msg = email.message_from_bytes(fetch_data[0][1])

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    html_content = part.get_payload(decode=True).decode(errors='ignore')
                    links.extend(get_links_from_html(html_content))
        else:
            content_type = msg.get_content_type()
            content = msg.get_payload(decode=True).decode(errors='ignore')

            if content_type == "text/html":
                links.extend(get_links_from_html(content))

    mail.logout()
    return links

def save_links(links):
    with open("links.txt", "w") as f:
        f.write("\n".join(links))

links = search_inbox()
for link in links:
    click_link(link)

save_links(links)
