import requests
import os

def grab_next_hour_price_prediction(token_address, chain):
    if chain == "ETH":
        pond_api=os.getenv("POND_API_ETH")
    elif chain == "BASE":
        pond_api=os.getenv("POND_API_BASE")
    else:
        raise ValueError("Not Yet Supported")
    
    latest_prediction = requests.get(pond_api+"predict/{}".format(token_address)).json()[0]
    return latest_prediction


def 