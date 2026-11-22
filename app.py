import os
import urllib.parse
from flask import Flask, render_template_string, request
from playwright.sync_api import sync_playwright

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google AI Mode Search</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
            background-color: #f8f9fa;
            color: #202124;
        }
        .search-box {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        input[type="text"] {
            flex: 1;
            padding: 12px 16px;
            font-size: 16px;
            border: 1px solid #dfe1e5;
            border-radius: 24px;
            outline: none;
        }
        button {
            padding: 12px 24px;
            font-size: 16px;
            background-color: #1a73e8;
            color: white;
            border: none;
            border-radius: 24px;
            cursor: pointer;
        }
        button:hover { background-color: #1557b0; }
        #loading {
            display: none;
            color: #5f6368;
            font-style: italic;
            margin-bottom: 15px;
        }
        .result-box {
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 1px 6px rgba(32,33,36,0.1);
            white-space: pre-wrap;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <h2>Google AI Mode Extractor</h2>
    <form method="POST" class="search-box" onsubmit="document.getElementById('loading').style.display='block'">
        <input type="text" name="query" placeholder="Ask anything..." value="{{ query }}" required>
        <button type="submit">Search</button>
    </form>

    <div id="loading">Launching browser and fetching AI response (takes ~10 seconds)...</div>

    {% if result %}
        <div class="result-box">{{ result }}</div>
    {% endif %}
</body>
</html>
"""

def get_google_ai_mode(query):
    encoded_query = urllib.parse.quote_plus(query)
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            page.goto(f"https://google.com{encoded_query}&hl=en", timeout=30000)
            page.wait_for_timeout(3000)

            if "sorry/index" in page.url or page.locator("text='unusual traffic'").is_visible():
                return "Blocked: Google detected cloud server traffic and triggered a CAPTCHA."

            ai_tab = page.locator("text='AI Mode'").first
            if ai_tab.is_visible():
                ai_tab.click()
                page.wait_for_timeout(6000)
                return page.locator("main").inner_text()

            aio = page.locator('[data-attrid="wa:/description"]').first
            if aio.is_visible():
                return aio.inner_text()

            return "AI Mode / AI Overview did not trigger for this query."

        except Exception as e:
            return f"Error: {str(e)}"
        finally:
            browser.close()

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    query = ""
    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if query:
            result = get_google_ai_mode(query)
    return render_template_string(HTML_TEMPLATE, result=result, query=query)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
