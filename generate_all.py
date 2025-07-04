from pathlib import Path
import shutil

# Define project base path
base_path = Path("ai_first_adv4_agent")

# File content definitions
files = {
    "main.py": '''
from agents.navigator_agent import AIAdvantageAgent

if __name__ == "__main__":
    task = "Log in to Advantage 4 and navigate to the GAX entry screen"
    agent = AIAdvantageAgent()
    agent.execute_task(task)
''',

    "agents/__init__.py": "",

    "agents/navigator_agent.py": '''
import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from strategies.planner import plan_steps
from dotenv import load_dotenv

load_dotenv()

class AIAdvantageAgent:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.url = os.getenv("ADV4_URL")

    def resolve_value(self, value):
        if isinstance(value, str) and value.startswith("env:"):
            return os.getenv(value.split(":", 1)[1])
        return value

    def execute_step(self, step):
        action = step.get("action")
        selector = step.get("selector")
        text = step.get("text")
        value = self.resolve_value(step.get("value", ""))

        if action == "go_to_url":
            self.driver.get(self.url)
        elif action == "click":
            if selector:
                el = self.driver.find_element(By.CSS_SELECTOR, selector)
                el.click()
            elif text:
                el = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{text}')]")
                el.click()
        elif action == "fill":
            el = self.driver.find_element(By.CSS_SELECTOR, selector)
            el.clear()
            el.send_keys(value)
        elif action == "press_enter":
            el = self.driver.find_element(By.CSS_SELECTOR, selector)
            el.send_keys(Keys.RETURN)
        time.sleep(2)

    def execute_task(self, task_description):
        self.driver.get(self.url)
        time.sleep(3)

        Path("screenshots").mkdir(exist_ok=True)
        html = self.driver.page_source
        with open("screenshots/current.html", "w", encoding="utf-8") as f:
            f.write(html)
        self.driver.save_screenshot("screenshots/current.png")

        print("🔄 Sending task to GPT...")
        plan = plan_steps(task_description, html)
        if not plan:
            print("❌ GPT did not return a valid plan.")
            return

        print(f"✅ Executing {len(plan)} steps.")
        for i, step in enumerate(plan):
            try:
                print(f"Step {i+1}: {step}")
                self.execute_step(step)
            except Exception as e:
                print(f"❌ Step failed: {step} – Error: {e}")
                self.driver.save_screenshot(f"screenshots/step_failed_{i+1}.png")
                break

        print("✅ Task completed or ended.")
        self.driver.quit()
''',

    "strategies/__init__.py": "",

    "strategies/planner.py": '''
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def plan_steps(task_description, html):
    prompt = f\"\"\"
You are an automation agent for the Advantage 4 (FINET) web application.

The user’s task is: "{task_description}"

You must start by navigating to the login URL and logging in using the provided credentials:
- Username: env:ADV_USER
- Password: env:ADV_PASS

Generate a list of JSON-formatted steps with:
- action: click, fill, go_to_url, press_enter
- selector: CSS selector (preferred)
- value: for fill actions
- text: optional fallback

Use the HTML snapshot below to help you identify login fields or labels:
{html[:10000]}
\"\"\"

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert UI automation planner."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        raw = response.choices[0].message.content.strip()
        return eval(raw, {"__builtins__": None}, {})
    except Exception as e:
        print("❌ GPT Planning failed:", e)
        return []
''',

    "requirements.txt": '''
selenium
openai>=1.0.0
python-dotenv
'''
}

# Write files to disk with safety checks and backup
for relative_path, content in files.items():
    full_path = base_path / relative_path
    full_path.parent.mkdir(parents=True, exist_ok=True)

    if full_path.exists():
        backup_path = full_path.with_suffix(".bak")
        shutil.copy(full_path, backup_path)
        print(f"🔁 Backed up existing {relative_path} to {backup_path.name}")

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip())
        print(f"✅ Wrote {relative_path}")
