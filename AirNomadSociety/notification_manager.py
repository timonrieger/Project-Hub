import json, smtplib, requests
from secrets import ANS_EMAIL, ANS_MAIL_PASSWORD

# import email.mime.text

BITLY_ACCESS_TOKEN = "#"
BITLY_ENDPOINT = "https://api-ssl.bitly.com/v4/shorten"

ALERTZY_ACCOUNT_KEY = "#"

TINYURL_ENDPOINT = "#"

class NotificationManager:
    #This class is responsible for sending notifications with the deal flight details.

    def __init__(self):
        self.message_body = ""

    def send_alertzy(self, message, destination, link):
        endpoint = "https://alertzy.app/send"
        parameters = {
            "accountKey": ALERTZY_ACCOUNT_KEY,
            "title": f"New Low Price Flight to {destination}",
            "message": message,
            "link": link,
            "group": "Flights",
        }

        requests.post(url=endpoint, params=parameters)

    def shorten_link_bitly(self, link):
        headers = {
            "Authorization": "Bearer " + BITLY_ACCESS_TOKEN,
            "Content-Type": 'application/json'
        }
        data = {"long_url": link}
        json_data = json.dumps(data)
        short_link = requests.post(url=BITLY_ENDPOINT, data=json_data, headers=headers).json()["link"]
        return short_link


    def send_emails(self, to_adress, message):
        try:
            with smtplib.SMTP_SSL(host="smtp.gmail.com") as connection:
                connection.login(user=ANS_EMAIL, password=ANS_MAIL_PASSWORD)
                connection.sendmail(
                    from_addr=ANS_EMAIL,
                    to_addrs=to_adress,
                    msg=f"Subject: New Low Price Flights!\n\n{message}".encode("UTF-8"))
        except smtplib.SMTPRecipientsRefused:
            print("You provided an invalid email adress.")

############### these ways did not work until now #############

        ############ parse the link via html, might work when i know more about html ###############
        #link = email.mime.text.MIMEText("u"f"<a href= {flight_link}>click here</a>", "html")
            #link = open(flight_link, "w").write(f'<a href={flight_link}> Link </a>')
            #email_body = message + link
            #link = f"\x1b]8;;{flight_link}\x1b\\Ctrl+Click here\x1b]8;;\x1b\\"

            # Email content with HTML for the clickable link
            #email_content = f"""
            #<html>
                #<body>
                    #<p>Click <a href="{flight_link}">here</a> for more details.</p>
                #</body>
            #</html>
            #"""

            # Create the MIMEText object
            #link = email.mime.text.MIMEText(email_content, 'html')


    #def create_tinyurl(self, link):
        #api_url = "http://tinyurl.com/api-create.php?url=" + link
        #response = requests.get(api_url)
        #return response.text


#from urllib.parse import quote
#link = "https://www.kiwi.com/deep?affilid=timonriegerflight1comparator&currency=EUR&flightsId=1dde03474d210000745f840d_0%7C03471dde4d2c00005406ae29_0&from=MUC&lang=en&passengers=1&to=TFS&booking_token=GtqYVIKcXTVLHE8e4fyiCuvIhcNph2HlihaLC7qEHxI_MsYvQAgfsNzFmJz1vr825PxlwNZyM4KLpeql1PGSJzKZlWS5qkTADORNG5B0CDkv-Y5NdiVYwPDRpIYxPSOledkGMQNN-bmzYthJ6TXJf5hVt8zf5LJwBY6O9I4GwZWBmICKukEVK0nR2bPMLEv2NX8y1VSfzP7_0n_eXq_r_CmLHPI7UIl3hDWUcC4PCuzWYQaKHJh1_DNePK-XQ0_WoOgpynhB8RjF-aZebpDITSlfubqsasd76QcpVOftnLQMWsAopbhYavJ2P6gCrnwdkMAhCtfILjaNqEW9ytVHC9Ls8o5fvkk8z7PIzugBzVQUfhlUTCP6MiUUEULd5GB71SIMt1bwu1CKXxOIHNZgNPLpwDiyine5rSiwZ4aZw2F23TOCCERCUEOkMEXcl-QQ195pQJkknHeL3tRMIkk35O9pgeP3bnhiOqoL79dCrvjNogmSexnYpgvhK8x9gKRdrNNUYIVnwKPP2v5mvOsdS_9odVrRFOaWd2zM2sXgtIbJ4tt0dIRmRc9R_g0swF1v4bpfDQizkJuAoC_4b0M7Oww=="
#encoded_link = quote(link, safe='')
#api_url = f"http://tinyurl.com/api-create.php?url={encoded_link}"
#response = requests.get(api_url)
#print(response.text)