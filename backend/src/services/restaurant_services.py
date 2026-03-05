from src.schemas.restaurant_schema import Restaurant
from src.repositories.restaurant_repo import RestaurantRepo

class RestaurantService:

    @staticmethod
    async def get_all_restaurants() -> list:
        restaurants = await RestaurantRepo.read_all()
        return restaurants

    # @staticmethod
    # async def get_restaurants_search(query: str) -> list:
    #     restaurants = await RestaurantRepo.read_all()
    #     results = []

    #     for restaurant in restaurants:
    #         if query in str(restaurant["restaurant_id"]): #will change to name once added
    #             results.append(restaurant)
    #     return results

    # @staticmethod
    # async def get_restaurants_search_advance(query: str, filters: list, sort: str) -> list:
    #     restaurants = await RestaurantRepo.read_all()
    #     query = query.casefold()
    #     results = []

    #     for restaurant in restaurants:
    #         attributes = [restaurant["cuisine"]] #will update with more filters once added
    #         matches_filter = False

    #         if query in str(restaurant["restaurant_id"]): #will change to name once added
    #             for search_filter in filters:
    #                 if search_filter in attributes: #will update
    #                     matches_filter = True
    #                     break
    #             if matches_filter:
    #                 results.append(restaurant)
        
    #     if sort == "AlphabetAsc":
    #         results.sort(key=lambda r: r.get("restaurant_id"),) #will change to name once added
    #     elif sort == "AlphabetDesc":
    #         results.sort(key=lambda r: r.get("restaurant_id"),
    #                      reverse=True) #will change to name once added
    #     elif sort == "RatingAsc":
    #         results.sort(key=lambda r: float(r.get("avg_ratings", 0)))
    #     elif sort == "RatingDesc":
    #         results.sort(key=lambda r: float(r.get("avg_ratings", 0)),
    #                      reverse=True)
    #     return results