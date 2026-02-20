from openai import AzureOpenAI
from config.settings import get_settings

settings = get_settings()

print(f"DEBUG: Endpoint is {settings.azure_openai_endpoint}")
print(f"DEBUG: Key starts with {settings.azure_openai_api_key[:4]}...")
client = AzureOpenAI(
    api_key=settings.azure_openai_api_key,
    api_version=settings.azure_openai_api_version,
    azure_endpoint=settings.azure_openai_endpoint,
)

# Test gpt-5-nano
response = client.chat.completions.create(
    model=settings.azure_openai_mini_deployment,
    messages=[{"role": "user", "content": "Say hello in one word."}],
    max_completion_tokens=10, # <--- The fix for GPT-5/o-series
)
print(f"gpt-5-nano: {response.choices[0].message.content}")
print(f"Tokens used: {response.usage.total_tokens}")

# Test gpt-5-mini
response = client.chat.completions.create(
    model=settings.azure_openai_chat_deployment,
    messages=[{"role": "user", "content": "Say hello in one word."}],
    max_completion_tokens=10,
)
print(f"gpt-5-mini: {response.choices[0].message.content}")
print(f"Tokens used: {response.usage.total_tokens}")

print("\nAzure setup complete!")