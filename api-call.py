import requests
import json



def get_api_data(url, parameters, header):
    response = requests.get(f"{url}", params=parameters, headers=header)
    if response.status_code == 200:
        print("sucessfully fetched the data with parameters")
        format_result(response.json())
    else:
        print(
            f"There's a {response.status_code} error with this request")

def format_result(data):
    text = json.dumps(data, sort_keys=True, indent=4)
    print(text)




if __name__ == "__main__":
    parameters = {
            
        }

    header={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8" , "Authorization":"Bearer CUTOuxWmuRfKQKynBGjFGmBROM9R"}
        
    api_call =  get_api_data("https://api.oregonstate.edu/v1/beaverbus/routes", parameters, header)
