# JobHound Bot

**Description:**

JobHound fetch job listings from individual servers, but it also has the ability to scrape across your entire Discord account, retrieving servers, channels, and job-related messages from multiple sources. By automating the process, it ensures that the latest job opportunities are sent directly to your Discord channel, making it an invaluable tool for job-focused communities.

---

## How to Use:

To fetch all the jobs in your server, simply import the bot and run the /work command. It will automatically gather and display all available job postings from your server.

If you want to retrieve job listings from across your entire Discord, set your authorization key and then run the /job command. This will scrape all the servers and channels you have access to and compile the job posts in one place.

---

## Installation:

- Ensure you have Python installed.
- Clone the repository.
- Set up the necessary environment variables (`BOT_TOKEN`, `AUTHORIZATION_KEY`).
- Install the required libraries:
  ```bash
  pip install discord requests selenium beautifulsoup4 spacy scikit-learn python-dotenv
  ```
- Download and set up Spacy's English language model:
  ```bash
  python -m spacy download en_core_web_sm
  ```
- Set up your Discord bot and retrieve the `BOT_TOKEN`.
- Run the bot:
  ```bash
  python bot.py
  ```
