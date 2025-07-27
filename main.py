import os
from google import genai
from google.genai import types
import json
import requests
from datetime import datetime

def fetch_wordle_data(date_str):
  url = f"https://www.nytimes.com/svc/wordle/v2/{date_str}.json"
  try:
    response = requests.get(url)
    response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
    return response.json()
  except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")
    return None

def generate(solution):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-flash"

    contents = f"""Role: You are a helpful Wordle hint generator bot. Your goal is to provide five progressively more specific clues for a secret five-letter Wordle word, without ever revealing the word itself.

Objective: For the five-letter Wordle word {solution}, generate 5 distinct hints. Each hint should build upon the previous one, making it progressively easier for a player to guess the word, but never directly revealing the word.

Target Audience: The hints should be easy to understand and appropriate for a 10-year-old. Use simple language and concepts they would be familiar with.

Constraints and Rules:

1. Absolutely No Direct Word Revelation (in hints): Under no circumstances should any hint, or any part of your response, explicitly state or directly imply the Wordle word. Be creative and indirect.

2. Increasing Specificity:

* Hint 1: Very broad and general. It should give a subtle clue about the word's category, common usage, or a very abstract concept related to it. It should be the least specific hint.

* Hint 2: Slightly more specific than Hint 1. It might narrow down the category or provide a more concrete, but still indirect, association.

* Hint 3: More specific than Hint 2. This hint could relate to a characteristic, a common phrase it's part of, or a more direct (but still abstract) definition.

* Hint 4: This hint MUST be the first letter of the Wordle word. Format it clearly (e.g., \"It starts with the letter 'X'.\").

* Hint 5: This hint MUST be the last letter of the Wordle word. Format it clearly (e.g., \"It ends with the letter 'Y'.\").

3. Five-Letter Words Only: Assume the word provided in {solution} will always be a five-letter English word.

4. Output Format: Present the hints as a JSON object named `hints`, which contains an array of all five hints.

Tone: Be helpful, slightly cryptic for the initial hints, and encouraging."""

    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type = genai.types.Type.OBJECT,
            properties = {
                "hints": genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    items = genai.types.Schema(
                        type = genai.types.Type.STRING,
                    ),
                ),
            },
        ),
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config
    )

    return response.text

if __name__ == "__main__":
    wordle_data = fetch_wordle_data(datetime.now().strftime('%Y-%m-%d'))
    solution = wordle_data['solution']

    hints = generate(solution)

    parsed_hints = json.loads(hints)

    html_template = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Daily Wordle Helper</title>
        <!-- Tailwind CSS CDN -->
        <script src="https://cdn.tailwindcss.com"></script>
        <!-- Michroma Font from Google Fonts -->
        <link href="https://fonts.googleapis.com/css2?family=Michroma&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Michroma', sans-serif;
                background-color: #0d0d0d;
                color: #e2e8f0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                padding: 20px;
                box-sizing: border-box;
            }}
            .container {{
                background-color: transparent;
                border-radius: 1.5rem;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.2);
                padding: 2.5rem;
                width: 100%;
                max-width: 600px;
                text-align: center;
                animation: fadeInContainer 0.8s ease-out;
            }}
            @keyframes fadeInContainer {{
                from {{ opacity: 0; transform: translateY(-20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}

            .hint-box {{
                background-color: transparent;
                border: 1px solid #4a4a4a;
                border-radius: 0.75rem;
                padding: 1.5rem;
                margin-bottom: 1.25rem;
                font-size: 1.125rem;
                color: #c8b653;
                font-weight: 600;
                min-height: 60px;
                display: flex;
                justify-content: center;
                align-items: center;
                opacity: 0;
                transform: translateY(20px);
                transition: transform 0.6s ease-out, height 0.6s ease-out, opacity 0.6s ease-out;
                overflow: hidden;
            }}

            .hint-box.revealed {{
                opacity: 1;
                transform: translateY(0);
            }}

            .hint-box.new-hint {{
                animation: slideInFromBottom 0.6s ease-out forwards;
            }}

            @keyframes slideInFromBottom {{
                from {{ opacity: 0; transform: translateY(30px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}

            .reveal-button {{
                background: linear-gradient(to right, #444444, #666666);
                color: white;
                padding: 1rem 2rem;
                border-radius: 9999px;
                font-weight: 600;
                font-size: 1.125rem;
                border: none;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.2);
            }}

            .reveal-button:hover {{
                transform: translateY(-3px);
                box-shadow: 0 15px 20px -5px rgba(0, 0, 0, 0.6), 0 6px 8px -3px rgba(0, 0, 0, 0.3);
                background: linear-gradient(to right, #555555, #777777);
            }}

            .reveal-button:active {{
                transform: translateY(0);
                box-shadow: 0 5px 10px -2px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.1);
            }}

            @media (max-width: 640px) {{
                .container {{
                    padding: 1.5rem;
                    border-radius: 1rem;
                }}
                h1 {{
                    font-size: 1.75rem;
                }}
                .hint-box {{
                    font-size: 1rem;
                    padding: 1rem;
                }}
                .reveal-button {{
                    padding: 0.8rem 1.5rem;
                    font-size: 1rem;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="text-4xl font-bold text-gray-100 mb-2">Daily Wordle Helper</h1>
            <p class="text-gray-400 text-lg mb-8">Wordle #{wordle_data['days_since_launch']}</p>

            <div id="hint-container">
            </div>

            <button id="reveal-button" class="reveal-button mt-6">Reveal first hint</button>
        </div>

        <script>
            const hints = [
                "{parsed_hints['hints'][0]}",
                "{parsed_hints['hints'][1]}",
                "{parsed_hints['hints'][2]}",
                "{parsed_hints['hints'][3]}",
                "{parsed_hints['hints'][4]}"
            ];
            const todayWordle = "{solution}";

            let currentHintIndex = 0;

            const revealButton = document.getElementById('reveal-button');
            const hintContainer = document.getElementById('hint-container');

            function scrambleText(text) {{
                if (!text) return "";
                let scrambled = '';
                const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';

                for (let i = 0; i < text.length; i++) {{
                    const char = text[i];
                    if (char === ' ') {{
                        scrambled += ' ';
                    }} else {{
                        const randomChar = alphabet[Math.floor(Math.random() * alphabet.length)];
                        scrambled += randomChar;
                    }}
                }}
                return scrambled;
            }}

            function createHintBox(index, isWordle = false) {{
                const newHintBox = document.createElement('div');
                newHintBox.id = `hint-box-${{index}}`;
                newHintBox.classList.add('hint-box', 'new-hint');

                let textToScramble = "";
                if (isWordle) {{
                    textToScramble = todayWordle;
                }} else if (index < hints.length) {{
                    textToScramble = hints[index];
                }}

                newHintBox.innerHTML = `<span class="scrambled-text">${{scrambleText(textToScramble)}}</span>`;
                hintContainer.appendChild(newHintBox);

                void newHintBox.offsetWidth;

                return newHintBox;
            }}

            function revealText(hintBoxElement, actualText, isWordleReveal = false) {{
                const textSpan = hintBoxElement.querySelector('.scrambled-text');
                if (textSpan) {{
                    textSpan.textContent = actualText;
                    if (isWordleReveal) {{
                        textSpan.style.color = '#6ca965';
                    }} else {{
                        textSpan.style.color = '#c8b653';
                    }}
                }}
            }}

            revealButton.addEventListener('click', () => {{
                if (currentHintIndex < hints.length) {{
                    const currentHintBox = document.getElementById(`hint-box-${{currentHintIndex}}`);
                    if (currentHintBox) {{
                        revealText(currentHintBox, hints[currentHintIndex]);
                        currentHintBox.classList.add('revealed');
                        currentHintBox.classList.remove('new-hint');
                    }}

                    if (currentHintIndex + 1 < hints.length) {{
                        createHintBox(currentHintIndex + 1);
                    }}

                    currentHintIndex++;

                    if (currentHintIndex < hints.length) {{
                        revealButton.textContent = `Reveal ${{getOrdinal(currentHintIndex + 1)}} hint`;
                    }} else {{
                        revealButton.textContent = 'Reveal solution';
                    }}
                }} else {{
                    const wordleBox = createHintBox(currentHintIndex, true);
                    revealText(wordleBox, todayWordle, true);
                    wordleBox.classList.add('revealed', 'font-bold', 'text-2xl');
                    wordleBox.style.color = '#6ca965';
                    wordleBox.classList.remove('new-hint');
                    revealButton.style.display = 'none';
                }}
            }});

            function getOrdinal(n) {{
                const s = ["th", "st", "nd", "rd"];
                const v = n % 100;
                return n + (s[(v - 20) % 10] || s[v] || s[0]);
            }}

            document.addEventListener('DOMContentLoaded', () => {{
                const initialHintBox = createHintBox(0);
                initialHintBox.classList.add('revealed');
                initialHintBox.classList.remove('new-hint');
            }});
        </script>
    </body>
    </html>
    """

    with open("status_report.html", "w", encoding="utf-8") as f:
        f.write(html_template)
