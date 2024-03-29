import time

from flight_search import FlightSearch

flight_search = FlightSearch()
iata_codes = []

# Sample text from the copied column
city_list = """Bangkok
Barcelona
Beijing
Chicago
London
Mexicali
Moscow
New York
Orlando
Osaka
Paris
Portland
Seoul
Siem Reap
Tehran"""

country_list = """Thailand
Spanien
China
USA
Vereinigtes Königreich
Mexiko
Russland
USA
USA
Japan
Frankreich
USA
Südkorea
Kambodscha
Iran"""

# Convert the string to a list of cities
cities = city_list.split('\n')
countries = country_list.split('\n')
print(cities)
print(countries)
# Iterate through each city
request_count = 0
for city in cities:
    index = cities.index(city)
    try:
        code = flight_search.get_destination_codes(city, countries[index])
    except IndexError or KeyError:
        print("No Airport")
    else:
        print(code)
        iata_codes.append(code)
        request_count += 1
        if request_count % 30 == 0:
            print("reloading request limit...")
            time.sleep(60)
print(iata_codes)
