import httpx

KITCHEN_CHAT = -4601874446
CASSIR_CHAT = -4775971943


async def get_api(path: str):
    async with httpx.AsyncClient() as client:
        return (await client.get(f'http://127.0.0.1:8000/{path}')).json()

async def post_api(path: str, json):
    async with httpx.AsyncClient() as client:
        return (await client.post(f'http://127.0.0.1:8000/{path}', json=json)).json()

async def patch_api(path: str, json):
    async with httpx.AsyncClient() as client:
        print(json)
        return (await client.patch(f'http://127.0.0.1:8000/{path}', json=json)).json()

async def delete_api(path: str):
    async with httpx.AsyncClient() as client:
        return (await client.delete(f'http://127.0.0.1:8000/{path}')).json()