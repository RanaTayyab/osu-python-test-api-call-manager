import requests
import json
import yaml


def load_config():
    with open("configuration.yaml", "r") as file:
        return yaml.safe_load(file)


def get_access_token():
    # Load configurations from the YAML file
    config = load_config()
    url = config["accessToken"]["url"]
    enhancer = config["accessToken"]["enhancer"]
    payload = config["accessToken"]["payload"]
    headers = config["accessToken"]["headers"]
    http_failed = config["httpResponses"]["failed"]

    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        # Request was successful
        access_token = response.json()["access_token"]
        if access_token:
            access_token = enhancer + access_token
        return access_token
    else:
        print(http_failed, response.status_code)


def get_api_data(url, parameters, header):
    config = load_config()
    http_success = config["httpResponses"]["success"]
    response = requests.get(f"{url}", params=parameters, headers=header)
    if response.status_code == 200:
        print(http_success)
        format_result(response.json())
    else:
        print(
            f"There's a {response.status_code} error with this request")


def format_result(data):
    text = json.dumps(data, sort_keys=True, indent=4)
    print(text)


def show_tasks():
    config = load_config()
    # Get the API options from the config
    apiOptions = config["apiOptions"]
    print(config["generalStrings"]["whichApi"])
    for i, option in enumerate(apiOptions, start=1):
        print(f"{i}. {option}")


def get_user_choice():
    config = load_config()
    choice = input(config["generalStrings"]["enterChoice"])
    return choice


def get_url(choice):
    config = load_config()
    if choice == "1":
        return config["apiUrls"]["beaverBus"]
    elif choice == "2":
        return config["apiUrls"]["terms"]
    elif choice == "3":
        print(config["generalStrings"]["exiting"])
    else:
        print(config["generalStrings"]["invalidChoice"])


if __name__ == "__main__":
    config = load_config()
    accessToken = get_access_token()
    contentType = config["accessToken"]["headers"]["Content-Type"]
    header = {"Content-Type": contentType, "Authorization": accessToken}

    while True:
        parameters = {
        }
        show_tasks()
        userChoice = get_user_choice()
        api_url = get_url(userChoice)
        if userChoice == "3":
            break
        if userChoice == "1" or userChoice == "2":
            api_call = get_api_data(api_url, parameters, header)
