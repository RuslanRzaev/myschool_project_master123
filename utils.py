import os
from dotenv import load_dotenv
import httpx

KITCHEN_CHAT = -4601874446
CASSIR_CHAT = -4775971943

load_dotenv()
api_token = os.getenv('API_TOKEN')
headers = {"Authorization": f"Bearer {api_token}"}


async def get_api(path: str, need_json=True):
    if need_json:
        async with httpx.AsyncClient() as client:
            return (await client.get(f'http://127.0.0.1:8000/{path}', headers=headers)).json()
    else:
        async with httpx.AsyncClient() as client:
            return (await client.get(f'http://127.0.0.1:8000/{path}', headers=headers))


async def post_api(path: str, json):
    async with httpx.AsyncClient() as client:
        return (await client.post(f'http://127.0.0.1:8000/{path}', json=json, headers=headers)).json()


async def patch_api(path: str, json):
    async with httpx.AsyncClient() as client:
        return (await client.patch(f'http://127.0.0.1:8000/{path}', json=json, headers=headers)).json()


async def delete_api(path: str):
    async with httpx.AsyncClient() as client:
        return (await client.delete(f'http://127.0.0.1:8000/{path}', headers=headers)).json()
