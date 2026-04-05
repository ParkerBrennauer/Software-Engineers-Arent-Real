class TipService:

    @staticmethod
    def calculate_tip(subtotal: float, tip_percent: float) -> float:
        if tip_percent < 0:
            raise ValueError("Tip percent cannot be negative")

        return round(subtotal * (tip_percent/100), 2)
