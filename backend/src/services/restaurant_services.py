from src.repositories.restaurant_repo import RestaurantRepo


class RestaurantService:
    @staticmethod
    async def get_all_restaurants() -> list:
        restaurants = await RestaurantRepo.read_all()
        return restaurants

    @staticmethod
    async def get_restaurants_search(query: str) -> list:
        restaurants = await RestaurantRepo.read_all()
        results = []

        for restaurant in restaurants:
            # will change to name once added
            if query in str(restaurant["restaurant_id"]):
                results.append(restaurant)
        return results

    @staticmethod
    async def get_restaurants_search_advance(query: str, filters: list, sort: str) -> list:
        restaurants = await RestaurantRepo.read_all()
        query = query.casefold()
        results = []

        for restaurant in restaurants:
            # will update with more filters once added
            attributes = [restaurant["cuisine"]]
            matches_filter = False

            # will change to name once added
            if query in str(restaurant["restaurant_id"]):
                for search_filter in filters:
                    if search_filter in attributes:  # will update
                        matches_filter = True
                        break
                if matches_filter:
                    results.append(restaurant)

        if sort == "AlphabetAsc":
            # will change to name once added
            results.sort(key=lambda r: r.get("restaurant_id"),)
        elif sort == "AlphabetDesc":
            results.sort(key=lambda r: r.get("restaurant_id"),
                         reverse=True)  # will change to name once added
        elif sort == "RatingAsc":
            results.sort(key=lambda r: float(r.get("avg_ratings", 0)))
        elif sort == "RatingDesc":
            results.sort(key=lambda r: float(r.get("avg_ratings", 0)),
                         reverse=True)
        return results
