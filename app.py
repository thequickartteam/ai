import os
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Free AI Mode Search (Puter.js)</title>
    <script src="https://puter.com"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 820px;
            margin: 40px auto;
            padding: 0 20px;
            background-color: #f8f9fa;
            color: #202124;
        }
        h2 { margin-bottom: 16px; }
        .controls {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
        }
        select {
            padding: 12px 16px;
            font-size: 15px;
            border: 1px solid #dfe1e5;
            border-radius: 24px;
            background-color: white;
            outline: none;
            cursor: pointer;
        }
        input[type="text"] {
            flex: 1;
            min-width: 240px;
            padding: 12px 18px;
            font-size: 16px;
            border: 1px solid #dfe1e5;
            border-radius: 24px;
            outline: none;
        }
        input[type="text"]:focus, select:focus { border-color: #1a73e8; }
        button {
            padding: 12px 24px;
            font-size: 16px;
            background-color: #1a73e8;
            color: white;
            border: none;
            border-radius: 24px;
            cursor: pointer;
            font-weight: 500;
        }
        button:hover { background-color: #1557b0; }
        button:disabled { background-color: #9aa0a6; cursor: not-allowed; }
        #status {
            color: #5f6368;
            font-size: 14px;
            margin-bottom: 12px;
            min-height: 20px;
        }
        .result-box {
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 1px 6px rgba(32,33,36,0.1);
            white-space: pre-wrap;
            line-height: 1.6;
            display: none;
        }
    </style>
</head>
<body>
    <h2>Free AI Search (No API Key)</h2>

    <div class="controls">
        <select id="modelSelect" title="Choose AI Model">
            <optgroup label="Google Gemini">
                <option value="google/gemini-2.5-flash" selected>Gemini 2.5 Flash (Fast & Free)</option>
                <option value="google/gemini-2.5-pro">Gemini 2.5 Pro</option>
                <option value="google/gemini-4-hydrogen">Gemini 4 Hydrogen</option>
            </optgroup>
            <optgroup label="OpenAI GPT">
                <option value="gpt-5-nano">GPT-5 Nano (Fast)</option>
                <option value="gpt-5-mini">GPT-5 Mini</option>
                <option value="gpt-4o-mini">GPT-4o Mini</option>
            </optgroup>
            <optgroup label="Open Models & Others">
                <option value="deepseek-chat">DeepSeek Chat</option>
                <option value="meta-llama/llama-4-maverick">Llama 4 Maverick</option>
                <option value="claude-sonnet-4">Claude Sonnet 4</option>
            </optgroup>
        </select>

        <input type="text" id="queryInput" placeholder="Ask anything..." required>
        <button id="searchBtn" onclick="askAI()">Ask</button>
    </div>

    <div id="status"></div>
    <div id="resultBox" class="result-box"></div>

    <script>
        const queryInput = document.getElementById("queryInput");
        const modelSelect = document.getElementById("modelSelect");
        const searchBtn = document.getElementById("searchBtn");
        const statusDiv = document.getElementById("status");
        const resultBox = document.getElementById("resultBox");

        queryInput.addEventListener("keypress", function(e) {
            if (e.key === "Enter") {
                e.preventDefault();
                askAI();
            }
        });

        async function askAI() {
            const prompt = queryInput.value.trim();
            const selectedModel = modelSelect.value;

            if (!prompt) return;

            searchBtn.disabled = true;
            statusDiv.textContent = `Generating response with ${selectedModel}...`;
            resultBox.style.display = "block";
            resultBox.textContent = "";

            try {
                const response = await puter.ai.chat(prompt, {
                    model: selectedModel,
                    stream: true
                });

                statusDiv.textContent = `Model: ${selectedModel}`;

                for await (const part of response) {
                    if (part?.text) {
                        resultBox.textContent += part.text;
                    }
                }
            } catch (err) {
                statusDiv.textContent = "Error occurred";
                resultBox.textContent = "Error: " + (err?.message || JSON.stringify(err));
            } finally {
                searchBtn.disabled = false;
            }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
