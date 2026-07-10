# UnsubEmail 📬🚫

A small Python script that scans your Gmail inbox for newsletter/marketing emails and automatically visits their "unsubscribe" links for you — so you don't have to click "unsubscribe" a hundred times by hand.

## What it does

- Logs into your Gmail account via IMAP
- Searches emails from the **last 15 days** that contain the word "unsubscribe"
- Parses the HTML body of each email and pulls out any links with "unsubscribe" in the URL or link text
- Sends a GET request to each unsubscribe link
- Saves every link it found to `links.txt`

## ⚠️ Disclaimer

- **I am not responsible if this tool deletes, modifies, or otherwise affects any important emails in your inbox.** Use at your own risk.
- **This tool is not guaranteed to work 100% of the time.** Some unsubscribe links require a confirmation click, a login, or POST/form submission instead of a simple GET request, and won't be fully processed. Always double check `links.txt` and your inbox afterward.
- It's strongly recommended you **back up important emails** and/or test on a secondary account first.

## Requirements

- Python 3.8+
- A **Google App Password** (see below — your normal Gmail password will not work)

### Python packages

```bash
pip install -r requirements.txt
```

If virtual environemnt errors are shown use these commands
```bash
python3 -m venv venv
source venv/bin/activate
```

## Setup

### 1. Create a Google App Password

App passwords let this script log in without using your real Gmail password. They only work if 2-Step Verification is turned on.

1. Turn on **2-Step Verification**: [myaccount.google.com/security](https://myaccount.google.com/security)
2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Create a new app password (name it something like "UnsubEmail")
4. Google will generate a **16-character password** — copy it, you won't be able to see it again

### 2. Create a `.env` file

In the project root, create a file named `.env`:

```env
EMAIL=your_email@gmail.com
PASSWORD=your_16_character_app_password
```

> Don't use quotes around the values, and don't commit this file — add `.env` to your `.gitignore`.

## Usage

```bash
git clone https://github.com/VihasMethnula/UnsubEmail.git
cd UnsubEmail

# create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate

pip install -r requirements.txt
# create your .env file as described above
python main.py
```

The script will:
1. Log in to your inbox
2. Search and process matching emails
3. Print each link it visits and whether it succeeded
4. Write all found links to `links.txt` in the project folder
