# import requests
# sheet_nr = 1
# SHEETY_ALL_ENDPOINT = "https://api.sheety.co/e2e4da57cedbf59fa0d734324f84fc00/flightDeals"
# user_data = requests.get(url=f"{SHEETY_ALL_ENDPOINT}/users").json()["users"]
#
# emails = []
# for user in user_data:
#     if user["email"] in emails:
#         print(user["email"])
#         print(user["id"])
#         requests.delete(url=f"{SHEETY_ALL_ENDPOINT}/destinations{sheet_nr}/{user["id"]}")
#     else:
#         emails.append(user["email"])

# import os
#
# variable = os.environ.get("SHEETY_BEARER")
# print(variable)
