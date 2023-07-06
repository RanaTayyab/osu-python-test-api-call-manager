import requests
import json
import yaml
import datetime
import pytz


def load_config():
    with open("configuration.yaml", "r") as file:
        return yaml.safe_load(file)


def log_error(error_message):
    # Get the current datetime in PST
    pst_timezone = pytz.timezone('America/Los_Angeles')
    current_time = datetime.datetime.now(pst_timezone)
    formatted_message = f"[{current_time}] {error_message}"

    # Append the error message to the logfile
    with open("logfile.txt", "a") as file:
        file.write(formatted_message + "\n")


def get_access_token():
    # Load configurations from the YAML file
    config = load_config()
    url = config["accessToken"]["url"]
    enhancer = config["accessToken"]["enhancer"]
    payload = config["accessToken"]["payload"]
    headers = config["accessToken"]["headers"]
    http_failed = config["httpResponses"]["failed"]

    response = requests.post(url, data=payload, headers=headers, timeout=10)

    if response.status_code == 200:
        # Request was successful
        access_token = response.json()["access_token"]
        if access_token:
            access_token = enhancer + access_token
        return access_token
    else:
        log_error(str(http_failed) + str(response.status_code))


def get_api_data(url, parameters, header):
    config = load_config()
    http_success = config["httpResponses"]["success"]
    response = requests.get(f"{url}", params=parameters, headers=header, timeout=10)
    if response.status_code == 200:
        format_result(response.json())
    else:
        generated_error = 'There is a ' + str(response.status_code) + ' error with this request'
        log_error(generated_error)


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
