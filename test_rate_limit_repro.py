import asyncio
import httpx

async def test_rate_limit():
    url = "http://localhost:8001/v1/transactions/user/1"
    print(f"Starting Rate Limit Test against {url}...")
    print(f"Limit is set to 50 requests per minute.")
    
    async with httpx.AsyncClient() as client:
        for i in range(50):
            try:
                response = await client.get(url)
                if response.status_code == 429:
                    print(f"FAILED: Request {i+1} was blocked prematurely!")
                    return
            except httpx.RequestError as e:
                print(f"Request error: {e}")
                return

        print("Sent 50 requests. Next one should be blocked.")

        try:
            response = await client.get(url)
            if response.status_code == 429:
                print("SUCCESS: Request 51 was blocked with 429 Too Many Requests.")
            else:
                print(f"FAILED: Request 51 was NOT blocked. Status: {response.status_code}")
        except httpx.RequestError as e:
            print(f"Request error: {e}")

if __name__ == "__main__":
    asyncio.run(test_rate_limit())
