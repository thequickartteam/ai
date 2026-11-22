import os
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Free AI Search (No API Key)</title>
    <script src="https://puter.com" defer></script>
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
            <optgroup label="Direct Free API (No Login / Never Blocked)">
                <option value="pollinations:openai" selected>Pollinations GPT (Instant & Keyless)</option>
                <option value="pollinations:gemini">Pollinations Gemini (Instant & Keyless)</option>
                <option value="pollinations:searchgpt">Pollinations SearchGPT (Web Search)</option>
            </optgroup>
            <optgroup label="Puter.js Models (Requires Puter Pop-up)">
                <option value="puter:google/gemini-2.5-flash">Puter: Gemini 2.5 Flash</option>
                <option value="puter:google/gemini-2.5-pro">Puter: Gemini 2.5 Pro</option>
                <option value="puter:gpt-5-nano">Puter: GPT-5 Nano</option>
                <option value="puter:deepseek-chat">Puter: DeepSeek Chat</option>
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
            const selection = modelSelect.value;

            if (!prompt) return;

            searchBtn.disabled = true;
            resultBox.style.display = "block";
            resultBox.textContent = "";

            try {
                if (selection.startsWith("pollinations:")) {
                    const modelName = selection.split(":")[1];
                    statusDiv.textContent = `Fetching response (${modelName})...`;

                    const res = await fetch("https://pollinations.ai", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            messages: [{ role: "user", content: prompt }],
                            model: modelName
                        })
                    });

                    if (!res.ok) throw new Error(`HTTP ${res.status}`);
                    const text = await res.text();
                    statusDiv.textContent = `Provider: Pollinations (${modelName})`;
                    resultBox.textContent = text;

                } else if (selection.startsWith("puter:")) {
                    if (typeof window.puter === "undefined") {
                        throw new Error("Puter.js script was blocked by your browser/ad-blocker or failed to load. Disable ad-blocker for this page or use a Pollinations model from the dropdown.");
                    }

                    const modelName = selection.split(":")[1];
                    statusDiv.textContent = `Generating response with ${modelName}...`;

                    const response = await window.puter.ai.chat(prompt, {
                        model: modelName,
                        stream: true
                    });

                    statusDiv.textContent = `Provider: Puter (${modelName})`;

                    for await (const part of response) {
                        if (part?.text) {
                            resultBox.textContent += part.text;
                        }
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
