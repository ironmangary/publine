from src.ai_utils import save_api_config
import os

def configure_ai_provider():
    print("\n🔧 Configure AI Provider")

    provider = input("Enter provider name (e.g. 'openai'): ").strip()
    api_key = input("Enter your API key: ").strip()
    model = input("Enter preferred model (e.g. 'gpt-4'): ").strip()

    # Optional: Basic check to make sure something was entered
    if not provider or not api_key or not model:
        print("⚠️ All fields are required. Configuration aborted.")
        return

    config = {
        "provider": provider,
        "api_key": api_key,
        "model": model
    }

    save_api_config(config)
    print("✅ AI provider configuration saved successfully.")
