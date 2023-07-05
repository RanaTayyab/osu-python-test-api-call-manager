import requests
import json




def get_access_token():
    url = "https://api.oregonstate.edu/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": "8HAveOfxhbEQBDD5sA0VCEKVs8AHBv6z",
        "client_secret": "tcGxL8lztWYQYjbm"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
    }

    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        # Request was successful
        access_token = response.json()["access_token"]
        return access_token
    else:
        print("Request failed with status code:", response.status_code)

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


def show_tasks():
    print("Which API data you want to check \n")
    print("1. Beavers Bus")
    print("2. Terms")
    print("3. Quit")

def get_user_choice():
    choice = input("Enter your choice (1 or 2 or 3): ")
    return choice

def get_url(choice):
    if choice == "1":
        url = "https://api.oregonstate.edu/v1/beaverbus/routes"
        return url
    elif choice == "2":
        url = "https://api.oregonstate.edu/v1/terms"
        return url
    elif choice == "3":
            print("Exisiting...")
    else:
        print("Invalid choice. Please try again.")



if __name__ == "__main__":

    access_token = get_access_token()

    access_token = "Bearer " + access_token

    header={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8" , "Authorization":access_token}


    while True:
        parameters = {
            
        }

        show_tasks()

        user_choice = get_user_choice()

        api_url = get_url(user_choice)

        if user_choice == "3":
            break

        api_call =  get_api_data(api_url, parameters, header)

            