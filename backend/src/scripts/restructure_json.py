import json

jsonPath = "backend/src/data/raw/deliveries.json"
restaurants = {}
items = {}
customers = {}
delivery = {}
orders = {}
reviews = {}

with open(jsonPath, "r") as file:
    allEntries = json.load(file)

for entry in allEntries:

    #---------- restaurant ----------
    restaurantId = entry["restaurant_id"]
    if restaurantId not in restaurants:
        restaurants[restaurantId] = {
            "order_ids":[],
            "ratings":{"5":0, "4":0, "3":0, "2":0, "1":0, "0":0}
        }
    
    restaurants[restaurantId]["order_ids"].append(entry["order_id"])

    if (entry["customer_rating"] == 5):
        restaurants[restaurantId]["ratings"]["5"] += 1
    elif (entry["customer_rating"] == 4):
        restaurants[restaurantId]["ratings"]["4"] += 1
    elif (entry["customer_rating"] == 3):
        restaurants[restaurantId]["ratings"]["3"] += 1
    elif (entry["customer_rating"] == 2):
        restaurants[restaurantId]["ratings"]["2"] += 1
    elif (entry["customer_rating"] == 1):
        restaurants[restaurantId]["ratings"]["1"] += 1
    elif (entry["customer_rating"] == 0):
        restaurants[restaurantId]["ratings"]["0"] += 1

    #---------- items ----------
    food_items = entry["food_item"]
    itemKey = f"{food_items}_{restaurantId}"

    if itemKey not in items:
        items[itemKey] = {
            "food_item": entry["food_item"],
            "restaurant_id": entry["restaurant_id"],
            "times_ordered": 0,
            "avg_rating": 0.00
        }
    
    items[itemKey]["times_ordered"] += 1
                                    # (currentAvg*oldCount) -> oldTotal + newValue -> newTotal/newCount -> newAvg
    items[itemKey]["avg_rating"] = ( (items[itemKey]["avg_rating"] * (items[itemKey]["times_ordered"] - 1)) + entry["customer_rating"] ) / items[itemKey]["times_ordered"]

    #---------- orders ----------
    orderId = entry["order_id"]
    if orderId not in orders:
        orders[orderId] = {
            "order_time": entry["order_time"],
            "order_value": entry["order_value"],
            "route_taken": entry["route_taken"],
        }

    #---------- reviews -----------
    if orderId not in reviews:
        reviews[orderId] = {
            "customer_rating": entry["customer_rating"],
            "food_temperature": entry["food_temperature"],
            "food_freshness": entry["food_freshness"],
            "packaging_quality": entry["packaging_quality"],
            "food_condition": entry["food_condition"],
            "customer_satisfaction": entry["customer_satisfaction"]
        }

    #---------- customer ----------
    customerId = entry["customer_id"]
    if customerId not in customers:
        customers[customerId] = {
            "age": entry["age"],
            "gender": entry["gender"],
            "location": entry["location"],
            "order_history": entry["order_history"],
            "preferred_cuisine": entry["preferred_cuisine"],
            "order_frequency": entry["order_frequency"],
            "loyalty_program": entry["loyalty_program"],
            "order_ids":[],
        }
    
    customers[customerId]["order_ids"].append(entry["order_id"])

    #---------- delivery ----------
    if orderId not in delivery:
        delivery[orderId] = {
            "delivery_method": entry["delivery_method"],
            "delivery_time": entry["delivery_time"],
            "delivery_distance": entry["delivery_distance"],
            "traffic_condition": entry["traffic_condition"],
            "weather_condition": entry["weather_condition"],
            "delivery_time_actual": entry["delivery_time_actual"],
            "delivery_delay": entry["delivery_delay"],
            "small_route": entry["small_route"], 
            "bike_friendly_route": entry["bike_friendly_route"],
            "route_type": entry["route_type"],
            "route_efficiency": entry["route_efficiency"],
            "predicted_delivery_mode": entry["predicted_delivery_mode"],
            "traffic_avoidance": entry["traffic_avoidance"]
        }


#---------- create new json files ----------
restaurantsPath = "backend/src/data/restaurants.json"
with open(restaurantsPath, "w", encoding="utf-8") as file:
    json.dump(restaurants, file, indent = 1)

itemsPath = "backend/src/data/items.json"
with open(itemsPath, "w", encoding="utf-8") as file:
    json.dump(items, file, indent = 1)

ordersPath = "backend/src/data/orders.json"
with open(ordersPath, "w", encoding="utf-8") as file:
    json.dump(orders, file, indent = 1)

reviewsPath = "backend/src/data/reviews.json"
with open(reviewsPath, "w", encoding="utf-8") as file:
    json.dump(reviews, file, indent = 1)

customersPath = "backend/src/data/customer.json"
with open(customersPath, "w", encoding="utf-8") as file:
    json.dump(customers, file, indent = 1)

deliveryPath = "backend/src/data/delivery.json"
with open(deliveryPath, "w", encoding="utf-8") as file:
    json.dump(delivery, file, indent = 1)