import os
from dotenv import load_dotenv
from selenium import webdriver
from strategies.planner import plan_steps
from strategies.executor import execute_steps

# Load environment variables from .env file
load_dotenv()

# Ask user for a task
task = input("📝 What would you like me to do? ")

# Launch browser
driver = webdriver.Chrome()

# Navigate to base URL (fallback)
base_url = os.getenv("ADV_URL")
if base_url:
    print(f"🌐 Navigating to base URL: {base_url}")
    driver.get(base_url)
else:
    print("❌ ADV_URL is missing in .env!")
    exit(1)

# Capture initial page source
html_snapshot = driver.page_source

# Plan steps using GPT
steps = plan_steps(task, html_snapshot)

# Execute planned steps
try:
    execute_steps(steps, driver)
except Exception as e:
    print("❌ Error during execution:", e)

input("✅ Task complete. Press Enter to close browser...")
driver.quit()
