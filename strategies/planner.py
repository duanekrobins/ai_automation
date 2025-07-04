import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def plan_steps(task_description, html):
    base_url = os.getenv("ADV_URL", "")
    
    prompt = f"""
You are an automation planner for the Advantage 4 (FINET) web app.

The user said: "{task_description}"

Start by going to this login URL (from env): {base_url}

Use these env keys if needed:
- username: env:ADV_USER
- password: env:ADV_PASS

Generate a valid JSON array of steps, each with:
- action: go_to_url, fill, click, press_enter
- selector: CSS selector (preferred)
- value: (for fill)
- label: (optional fallback if selector is not known)

If unsure of selector, use:
- label: "Username", "Password", "Login", etc.
⚠️ Respond with JSON array ONLY (no commentary or markdown).

Snapshot of page HTML for context (first 10k chars):
{html[:10000]}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a smart UI automation planner that generates JSON instructions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )

        raw = response.choices[0].message.content.strip()
        print("\n🧾 Raw GPT Output:\n", raw)

        start = raw.find('[')
        end = raw.rfind(']')
        if start != -1 and end != -1:
            return json.loads(raw[start:end+1])

        print("⚠️ GPT output does not contain a JSON array.")
        return []

    except Exception as e:
        print("❌ GPT Planning failed:", e)
        return []
