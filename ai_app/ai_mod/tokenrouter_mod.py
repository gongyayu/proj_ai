import os
from tokenrouter import TokenRouter, AuthenticationError, RateLimitError
from dotenv import load_dotenv
import streamlit as st

# Initialize the client with your API key
# You can also set TOKENROUTER_API_KEY in your environment

load_dotenv(override=True)
TOKENROUTER_API_KEY = os.getenv("TOKENROUTER_API_KEY")

client = TokenRouter(
    api_key=TOKENROUTER_API_KEY,  # Get from Console → API Keys [citation:4]
    # Or localhost for self-hosted [citation:2][citation:11]
    base_url="https://api.tokenrouter.com/v1"
)


def send_routed_request(prompt, mode="balanced"):
    """
    Send a request with intelligent routing.

    Modes:
    - "balanced": Balance speed, cost, and quality
    - "cost": Minimize cost
    - "quality": Maximize quality
    - "fast": Prioritize speed [citation:3]
    """
    try:
        response = client.chat.completions.create(
            model="z-ai/glm-5.3-free",  # Let TokenRouter pick the best model
            mode=mode,     # Routing strategy
            model_preferences=["z-ai/glm-5.3-free"],
            messages=[
                # {"role": "developer", "content": "You are a helpful assistant."},
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            # Optional: pass provider keys inline for BYOK [citation:2]
            # key_mode="inline",
        )

        # Response includes standard OpenAI format plus extra metadata [citation:2]
        # print(f"Response: {response.choices[0].message.content}")
        # print(f"Routed to: {response.routed_provider}/{response.routed_model}")
        # print(f"Cost: ${response.cost_usd:.6f}")
        # print(f"Latency: {response.latency_ms}ms")
        st.code(response)
        return response

    except AuthenticationError:
        print("Invalid API key. Check your TokenRouter credentials.")
    except RateLimitError as e:
        print(f"Rate limited. Retry after: {e.retry_after}s")
    except Exception as e:
        print(f"Error: {e}")
