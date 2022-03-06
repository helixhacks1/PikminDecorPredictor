
from decor_type import DecorType

osm_decors_to_tags = {
    DecorType.restaurant: [("amenity", "restaurant")],
    DecorType.cafe: [("amenity", "cafe"), ("cuisine", "coffee_shop")],
    DecorType.sweetshop: [("shop", "pastry")],
    DecorType.movie_theater: [("amenity", "cinema")],
    DecorType.pharmacy: [("amenity", "pharmacy")],
    DecorType.zoo: [("tourism", "zoo")],
    DecorType.forest: [("natural", "wood"), ("landuse", "forest")],
    # both are used in different areas, so assume both, although theres less evidence for landuse=forest
    # ref: https://wiki.openstreetmap.org/wiki/Forest

    DecorType.waterside: [("natural", "water")],
    DecorType.post_office: [("amenity", "post_office")],
    DecorType.art_gallery: [("shop", "art")],
    DecorType.airport: [("aeroway", "aerodrome"), ("aeroway", "heliport")], # heliport not proven
    DecorType.station: [("railway", "station"), ("building", "train_station")],
    DecorType.beach: [("natural", "beach")],
    DecorType.burger_place: [("amenity", "fast_food"), ("cuisine", "burger")],
    DecorType.mini_mart: [("shop", "convenience")],
    DecorType.supermarket: [("shop", "supermarket")],
    DecorType.bakery: [("shop", "bakery"), ("cuisine", "pretzel")],
    # cuisine not proven, but theres a fair amount of evidence in a small dataset towards it.
    # or maybe theres just more pretezel shops in the world than I expect. Who knows.

    DecorType.hair_salon: [("shop", "hairdresser")],
    DecorType.clothes_store: [("shop", "clothes"), ("shop", "shoes")],
    DecorType.park: [("leisure", "park")]
}

foursquare_decors_to_tags = {
    DecorType.restaurant: ["Restaurant", "Buffet", "Diner", "Bar", "Pizzeria", "Steakhouse",
                           "Food and Beverage Retail", "African Restaurant", "American Restaurant",
                           "Chinese Restaurant", "Hawaiian Restaurant", "Italian Restaurant",
                           "Indian Restaurant", "Mexican Restaurant", "Middle Eastern Restaurant",
                           "Seafood Restaurant"],
    DecorType.cafe: ["Café", "Coffee Shop", "Cafes, Coffee, and Tea Houses"],
    DecorType.sweetshop: ["Dessert Shop"],
    DecorType.movie_theater: ["Movie Theater"],
    DecorType.pharmacy: ["Drugstore"],
    # no examples of zoo yet
    # no examples of forest yet
    # skip waterside
    DecorType.post_office: ["Post Office"],
    DecorType.art_gallery: ["Art Museum", "Art School"],
    # no examples of airports
    DecorType.station: ["Tram Station", "Rail Station"],
    # no examples of beach
    DecorType.burger_place: ["Fast Food Restaurant", "Burger Joint"],
    DecorType.mini_mart: ["Convenience Store"],
    DecorType.supermarket: ["Grocery Store / Supermarket"],
    DecorType.bakery: ["Bakery"],
    DecorType.hair_salon: ["Hair Salon", "Barbershop", "Health and Beauty Service"],
    DecorType.clothes_store: ["Clothing Store", "Shoe Store", "Fashion Retail"],
    DecorType.park: ["Park"]
}

yelp_decors_to_tags = {
    DecorType.restaurant: ["chinese", "steak", "sandwiches", "pizza", "bars",
                           "mexican", "buffets", "sandwiches", "tradamerican",
                           "newamerican", "icecream", "italian", "serbocroatian",
                           "mediterranean", "bbq", "hawaiian", "restaurants"],
    DecorType.cafe: ["cafes", "coffee"],  # coffeeroasteries maybe?
    DecorType.sweetshop: ["desserts", "customcakes"],
    # customcakes, cupcakes, juicebars all show up with not enough samples to be sure
    DecorType.movie_theater: ["movietheaters"],
    DecorType.pharmacy: ["drugstores"],
    # no examples of zoo yet
    # no examples of forest yet
    # skip waterside
    # no clear samples of post office
    DecorType.art_gallery: ["galleries", "artschools", "artclasses"],
    # no examples of airports
    DecorType.station: ["trainstations"],
    # no examples of beach
    DecorType.burger_place: ["burgers"],  # should look into {'alias': 'hotdogs', 'title': 'Fast Food'}
    DecorType.mini_mart: ["convenience"],
    DecorType.supermarket: ["grocery"],
    DecorType.bakery: ["bakeries"],  # some evidence of "donuts"
    DecorType.hair_salon: ["hair", "barbers", "menshair"],
    DecorType.clothes_store: ["shoes", "menscloth", "womenscloth", "sportswear", "leather"]
    # no clear samples of parks
}


google_places_decors_to_tags = {
    DecorType.restaurant: ["restaurant"],
    DecorType.cafe: ["cafe"],
    # no known sweetshop
    DecorType.movie_theater: ["movie_theater"],
    DecorType.pharmacy: ["drugstore", "pharmacy"],
    # no examples of zoo yet
    # no examples of forest yet
    # skip waterside
    # no known post office
    DecorType.art_gallery: ["art_gallery"],
    # no examples of airports
    DecorType.station: ["transit_station"],
    # no examples of beach
    # no known burger place
    DecorType.mini_mart: ["convenience_store"],
    DecorType.supermarket: ["grocery_or_supermarket", "supermarket"],
    DecorType.bakery: ["bakery"],
    DecorType.hair_salon: ["beauty_salon", "hair_care"],
    DecorType.clothes_store: ["shoe_store", 'clothing_store']
    # no known park
}
