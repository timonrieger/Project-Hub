import requests, os
from secret_keys import SHEETY_BEARER
from main import app, db, AirNomads
from secret_keys import TRAVEL_DATA

SHEETY_ALL_ENDPOINT = "https://api.sheety.co/e2e4da57cedbf59fa0d734324f84fc00/flightDeals"

HEADER = {
    "Authorization": f"Bearer {SHEETY_BEARER}"
}

class DataManager:
    # This class is responsible for talking to the Google Sheet.

    def __init__(self):
        self.destination_data = {}
        self.user_data = {}


    def get_user_data(self):
        with app.app_context():
            user_data = db.session.query(AirNomads).all()
        self.user_data = [{"username": user.username, "email": user.email, "departureCity": user.departure_city,
                           "departureIata": user.departure_iata, "currency": user.currency,
                           "nightsFrom": user.min_nights, "nightsTo": user.max_nights,
                           "dreamPlaces": user.travel_countries.split(",")[:-1]} for user in user_data] # Exclude the last empty string
        return self.user_data

    def get_destination_data(self):
        self.destination_data = requests.get(url=TRAVEL_DATA).json()["countries"]
        return self.destination_data

    ################# these methods are not used right now, but might be relevant in future updates ################

    def delete_duplicate_users(self):
        emails = []
        for user in self.user_data:
            if user["email"] in emails:
                row = emails.index(user["email"]) + 3
                requests.delete(url=f"{SHEETY_ALL_ENDPOINT}/users/{row}", headers=HEADER)
            emails.append(user["email"])

    def update_iata_code(self, iata_code, row, sheet_nr):
        new_data = {
            f"destinations{sheet_nr}": {
                "iataCode": iata_code
            }
        }
        requests.put(url=f"{SHEETY_ALL_ENDPOINT}/destinations{sheet_nr}/{row}", json=new_data)

    def update_price_goal(self, new_price_goal, row, sheet_nr):
        new_data = {
            f"destinations{sheet_nr}": {
                "lowestPrice": new_price_goal
            }
        }

        requests.put(url=f"{SHEETY_ALL_ENDPOINT}/destinations{sheet_nr}/{row}", json=new_data)
        return new_data

    def delete_city(self, row, sheet_nr):
        requests.delete(url=f"{SHEETY_ALL_ENDPOINT}/destinations{sheet_nr}/{row}")


    def delete_sent_sign(self):
        # deletes yes sign after all emails are sent
        for user in self.user_data:
            new_data = {
                "user": {
                    "sent": ""
                }
            }
            # requests.put(url=f"{SHEETY_PRICES_ENDPOINT}/{user["id"]}", json=new_data)

    def put_sent_sign(self, row):
        for user in self.user_data:
            new_data = {
                "user": {
                    "sent": "yes"
                }
            }
            #requests.put(url=f"{SHEETY_DESTINATIONS1_ENDPOINT}/{row}", json=new_data)


########## test if sheety is usable ################

# response = requests.get(url=f"{SHEETY_ALL_ENDPOINT}/users", headers=HEADER)
# if response.status_code != 200:
#     print(response.text)
#     exit()
# else:
#     print(response.json())