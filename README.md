# Chatbot Selenium Tester

A Selenium-based end-to-end test harness for a web **chatbot**. It drives a real
browser through chat conversations, feeding job ads / titles to the bot and
recording the bot's responses to a CSV so you can spot regressions in
conversation flows at scale.

Originally written to test a job-application assistant, it's a useful pattern
for anyone doing automated, browser-level QA of a conversational UI.

## How it works

- `main.py` - drives the browser: sends inputs, reads bot replies, classifies
  outcomes (success / wrong job title / unsupported / failure) and logs results
- `download.py` / `extract.py` - fetch the list of positions/titles to test
  (optionally from S3) and the latest job ads
- `setup.py` - output/file setup
- `clear_all.py` - reset helper
- `settings.py` - `test_url`, sleep interval, data source toggles

## Setup

```bash
pip install -r requirements.txt
# Download a chromedriver matching your Chrome version and put it on PATH
```

Edit `settings.py`:

```python
test_url = "YOUR_APP_HOST"          # the chatbot URL to test
get_latest_positions_from_s3 = False # or True if you wire up S3
```

Run:

```bash
python main.py        # results written to output.csv
```

> The CSS/element selectors in `main.py` are specific to the original chat UI -
> update the `find_element*` calls to match your app's DOM.

## License

MIT - see [LICENSE](LICENSE).
