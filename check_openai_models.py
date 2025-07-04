import os
from dotenv import load_dotenv
from openai import OpenAI

# ✅ Load variables from .env file
load_dotenv()

# ✅ Initialize client with API key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ List and print all available model IDs
models = client.models.list()
print("\n✅ Available models:")
for m in models.data:
    print("-", m.id)
