import aiohttp
from typing import Optional, List, Dict, Any

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Any:
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.base_url}{endpoint}"
        async with self.session.request(method, url, json=data) as response:
            if response.status >= 400:
                raise Exception(f"API request failed: {await response.text()}")
            return await response.json()

    # Методы для работы с пользователями
    async def create_user(self, tg_id: int):
        return await self._make_request("POST", "/users/", {"tg_id": tg_id})

    async def get_users(self):
        return await self._make_request("GET", "/users/")

    # Методы для работы с категориями
    async def get_categories(self):
        return await self._make_request("GET", "/categories/")

    async def create_category(self, name: str):
        return await self._make_request("POST", "/categories/", {"name": name})

    # Методы для работы с товарами
    async def get_items(self, category_id: int):
        return await self._make_request("GET", f"/items/category/{category_id}")

    async def create_item(self, item_data: Dict):
        return await self._make_request("POST", "/items/", item_data)

    # Методы для работы с корзиной
    async def add_to_basket(self, user_id: int, item_id: int):
        return await self._make_request("POST", "/basket/add", {
            "user_id": user_id,
            "item_id": item_id
        })

    async def get_basket(self, user_id: int):
        return await self._make_request("GET", f"/basket/{user_id}")

    # Методы для работы с заказами
    async def create_order(self, user_id: int, items: str, price: float, revenue: float):
        return await self._make_request("POST", "/orders/", {
            "user_id": user_id,
            "items": items,
            "price": price,
            "revenue": revenue
        })

    async def get_user_orders(self, user_id: int):
        return await self._make_request("GET", f"/orders/user/{user_id}")

    async def get_latest_order(self, user_id: int):
        return await self._make_request("GET", f"/orders/latest/{user_id}")

    # Методы для статистики
    async def get_daily_statistics(self):
        return await self._make_request("GET", "/statistics/orders/day")

    async def get_monthly_statistics(self):
        return await self._make_request("GET", "/statistics/orders/month") 