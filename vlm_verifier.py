# vlm_verifier.py
import anthropic
import base64
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def verify_medicine(image_path: str, medicine: str) -> bool:
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=10,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": img_b64
                    }
                },
                {
                    "type": "text",
                    "text": f"Is there a {medicine} medicine box clearly visible with its label? Reply only: true or false"
                }
            ]
        }]
    )
    result = response.content[0].text.strip().lower()
    print(f"VLM says: {result}")
    return result == "true"
