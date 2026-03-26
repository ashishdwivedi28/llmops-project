import asyncio
import json
import httpx

async def test():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://127.0.0.1:8000/invoke",
                json={"app_id": "default_llm", "user_input": "Hello, how are you?", "model": "gemini-2.5-flash"},
                timeout=30.0
            )
            print("Status:", response.status_code)
            print("Response:", json.dumps(response.json(), indent=2))
        except Exception as e:
            print("Error connecting to backend:", e)

if __name__ == "__main__":
    asyncio.run(test())
