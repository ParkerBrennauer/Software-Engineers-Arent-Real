class OrderRepo:
    FilePath = "orders.json"

    @classmethod
    async def save_order(cls, order_data: dict) -> dict:
        pass

    @classmethod
    async def get_by_id(cls, order_id: int) -> dict:
        pass
