from service.data_processing import calculate_total_distance
coordinates = [
    [52.2296756, 21.0122287],  # Titik awal (Warsaw, Poland)
    [52.406374, 16.9251681],   # Titik kedua (Poznan, Poland)
    [52.5200066, 13.404954],   # Titik ketiga (Berlin, Germany)
    [48.856614, 2.3522219],    # Titik keempat (Paris, France)
]

print(calculate_total_distance(coordinates))