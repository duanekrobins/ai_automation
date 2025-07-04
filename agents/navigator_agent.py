import os
import time
import json
from pathlib import Path  # ✅ add this
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
