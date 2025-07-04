import os
import time
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

load_dotenv()

def resolve_env(value):
    """
    Replaces 'env:KEY' with the corresponding environment variable value.
    """
    if isinstance(value, str) and value.startswith("env:"):
        return os.getenv(value[4:], "")
    return value

def find_by_label(driver, label):
    """
    Attempts to find an input element by its associated <label> text.
    """
    try:
        labels = driver.find_elements(By.TAG_NAME, "label")
        for lbl in labels:
            if label.lower() in lbl.text.lower():
                html_for = lbl.get_attribute("for")
                if html_for:
                    return driver.find_element(By.ID, html_for)
    except Exception:
        return None
    return None

def execute_steps(steps, driver):
    """
    Executes a sequence of UI automation steps using Selenium.
    Supports actions: go_to_url, click, fill, press_enter.
    """
    for i, step in enumerate(steps, start=1):
        print(f"\n🔹 Step {i}: {step}")
        try:
            action = step.get("action")
            selector = step.get("selector", "")
            value = resolve_env(step.get("value", ""))
            label = step.get("label", "")

            element = None

            # Determine the element to act on
            if selector:
                element = driver.find_element(By.CSS_SELECTOR, selector)
            elif label:
                element = find_by_label(driver, label)

            # Handle each action
            if action == "go_to_url":
                if not value.startswith("http"):
                    print(f"❌ Invalid or missing URL: '{value}'. Check your .env file.")
                    continue
                print(f"🌐 Navigating to URL: {value}")
                driver.get(value)
                time.sleep(3)

            elif action == "fill" and element:
                print(f"📝 Filling input with value: {value}")
                element.clear()
                element.send_keys(value)

            elif action == "click" and element:
                print("🖱️ Clicking element.")
                element.click()

            elif action == "press_enter" and element:
                print("↩️ Pressing ENTER.")
                element.send_keys(Keys.RETURN)

            else:
                print(f"⚠️ Unsupported or missing action/element: {action}")

            time.sleep(1)

        except Exception as e:
            print(f"❌ Step failed: {step} – Error: {e}")
