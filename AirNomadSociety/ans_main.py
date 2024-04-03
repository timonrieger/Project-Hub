##### Ideen als Add On
# Email Adresse beim Eingang mit "Air Nomad Society" erkennbar ❌
# Code in Python Anywhere einspeisen
# ich will ja nicht bei jedem flug für jeden nutzer einen eigenen link über bitly erstellen: entweder abo kaufen oder andere lösung finden (kein short link; anderer link shortener (tiny url geht ned), html code oder alle user mit dem gleichen flug durchgehen und so links sparen. https://t.ly/docs, wsl doch bitly oder einach gar nicht verkürzen (dann nur email möglich)
# Unsubscribe funktion (Name, vName, email, try delete, html)
# bei fav countries preisdifferenz zur vorwoche angeben ( macht das sinn bei sich ändernden städten ? )
# email übersetzen
# sheety template zur aquisition
# iata code verknüpfung (entweder in input formular ergänzen und dann per split aufteilen, oder in anderem sheet nach stadt suchen und iata code finden)

from datetime import datetime, timedelta
import random, time

from data_manager import DataManager
from flight_search import FlightSearch
from notification_manager import NotificationManager

data_manager = DataManager()
flight_search = FlightSearch()
notification_manager = NotificationManager()

# reloading_requests = 0
start_time = time.time()

data_manager.get_user_data()
weekday = 1  # datetime.now().strftime("%w")
data_manager.get_destination_data(sheet_nr=weekday)

for user in data_manager.user_data:
    selected_gems = random.sample(data_manager.destination_data, 5)
    message = f"Hey {user["username"]}!\n\n"
    dream_places = "🌟 Your Dream Destinations 🌟\n\n"
    dream_cities = []
    gem_places = "💎 Discover Hidden Gems 💎\n\n"

    for destination in data_manager.destination_data:
        # reloading_requests += 1
        if destination["country"] == "" and destination["iataCode"] == "":
            pass  # in case there is an empty line, skip this destination

        if destination["country"] in user.values():
            flight = flight_search.check_flight(
                departure_iata_code=user["departureIata"],
                arrival_iata_code=destination["code"],
                from_time=datetime.now() + timedelta(days=1),
                to_time=datetime.now() + timedelta(days=180),
                min_nights=user["nightsFrom"],
                max_nights=user["nightsTo"],
                currency=user["currency"].upper()
            )
            if flight is None:
                continue

            if flight.departure_city[0] != flight.arrival_city[0]:
                dream_places += (
                    f"✈️ Only {flight.price[0]}{flight.currency} to fly from "
                    f"{flight.departure_city[0]} ({flight.departure_iata_code[0]}) to "
                    f"{flight.arrival_city[0]} ({flight.arrival_iata_code[0]}), {flight.arrival_country}, "
                    f"from {flight.from_date[0]} to {flight.to_date[0]}.")
                if flight.stop_overs[0] > 0:
                    dream_places += f"Flight has {flight.stop_overs[0]} stop over in {flight.via_city}."
                dream_places += "\n"
                dream_cities.append(flight.arrival_city[0])

    for destination in selected_gems:
        flight = flight_search.check_flight(
            departure_iata_code=user["departureIata"],
            arrival_iata_code=destination["code"],
            from_time=datetime.now() + timedelta(days=1),
            to_time=datetime.now() + timedelta(days=180),
            min_nights=user["nightsFrom"],
            max_nights=user["nightsTo"],
            currency=user["currency"].upper()
        )
        if flight is None:
            continue

        if flight.departure_city[0] != flight.arrival_city[0] and flight.arrival_city[0] not in dream_cities:
            gem_places += (
                f"✈️ Only {flight.price[0]}{flight.currency} to fly from "
                f"{flight.departure_city[0]} ({flight.departure_iata_code[0]}) to "
                f"{flight.arrival_city[0]} ({flight.arrival_iata_code[0]}), {flight.arrival_country}, "
                f"from {flight.from_date[0]} to {flight.to_date[0]}.")
            if flight.stop_overs[0] > 0:
                gem_places += f" Flight has {flight.stop_overs[0]} stop over in {flight.via_city}."
            gem_places += "\n"

            # shorten link ###is working 12 links per month on bitly
            # link = notification_manager.create_tinyurl(flight.link)
            # print(flight.link)
            # places += f"\nBook now: {flight.link}\n\n"

    message += f"{dream_places}\n\n{gem_places}\n\nHappy Travels!\n\n"
    notification_manager.send_emails(to_adress=user["email"], message=message)
    # notification_manager.send_alertzy(message=message, destination=flight.arrival_city[0], link=flight.link)

    print(f"Code Runt Time was: {time.time() - start_time} seconds.")


    # if reloading_requests % 10 == 0:
    #    time.sleep(30)

# 2nd block in destination for loop (cut out because iata code won't be empty)
# elif destination["iataCode"] == "":
#    print("iata Code is empty")
#    try:
#        new_iata_code = flight_search.get_destination_codes(destination["city"], country_name=destination["country"])  # adds iata code to sheet data
#    except IndexError:
#        print("The arrival city you provided has no airport or is not existing.")
#        data_manager.delete_city(row=destination["id"], sheet_nr=weekday)  # delete row out of the google sheet ### maybe ask to replace ???
#        pass
#    else:
#        #data_manager.destination_data = sheet_data  # updates the iata code in sheet data
#        data_manager.update_iata_code(iata_code=new_iata_code, row=destination["id"], sheet_nr=weekday)  # updates the google sheet
#        ### please check if the iata code is updated in the google sheet and there is no endless loop bc the for loop does not recognize the change
#        # -> is ja kein while sondern if, deswegen alles easy :)
