from src.repositories.discount_repo import DiscountRepo

class DiscountServices:

    @staticmethod
    async def applyDiscount(order_total: float, discount_code: str) -> float | None:
        discount = await DiscountRepo.find_savings(discount_code)

        if discount is None:
            return None

        return round(order_total * discount, 2)

    @staticmethod
    async def createDiscount(discount_rate: float, discount_name: str, restaurant_id: int) -> str:
        discountcode = {
            discount_name: {
                "restaurant_id": restaurant_id,
                "discount_rate": discount_rate
            }
        }
        await DiscountRepo.save_code(discountcode)

        if await DiscountRepo.check_real(discount_name):
            return "valid code, enjoy saving"
        else:
            return "code is invalid"

    @staticmethod
    async def removeDiscount(discount_code: str) -> str:
        removed = await DiscountRepo.remove_code(discount_code)

        if removed:
            return "successfully removed code"
        else:
            return "Discount not found"