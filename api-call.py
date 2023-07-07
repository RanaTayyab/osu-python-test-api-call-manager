import datetime
import json

import pytz
import requests
import yaml


def load_from_config():
    """Loading important parameters from configuration file

    :returns: The config object
    """

    with open('configuration.yaml', 'r') as file:
        return yaml.safe_load(file)


def log_error(error_message):
    """Logging any error messages in the file and appending
    with date time information in PST

    :param error_message: The error message to log in file comes as a string
    """

    # Get the current datetime in PST
    pst_timezone = pytz.timezone('America/Los_Angeles')
    current_time = datetime.datetime.now(pst_timezone)
    formatted_message = f"[{current_time}] {error_message}"

    # Append the error message to the logfile
    with open('logfile.txt', 'a') as file:
        file.write(formatted_message + '\n')


def get_access_token():
    """Get access token from OAuth2 for connecting with OSU public APIs

    :returns: The access token string
    """

    # Load configurations from the YAML file
    config = load_from_config()
    url = config['accessToken']['url']
    enhancer = config['accessToken']['enhancer']
    payload = config['accessToken']['payload']
    headers = config['accessToken']['headers']
    http_failed = config['httpResponses']['failed']

    response = requests.post(url,
                             data=payload,
                             headers=headers,
                             timeout=10)

    if response.status_code == 200:
        # Request was successful
        access_token = response.json()['access_token']
        if access_token:
            access_token = enhancer + access_token
        return access_token
    else:
        log_error(str(http_failed) + str(response.status_code))


def get_api_data(url, parameters, header):
    """Get Request for getting the data from API

    :param url: URL of the API
    :param parameters: The parameters for API
    :param header: The headers for API with authorization
    """

    response = requests.get(f"{url}",
                            params=parameters,
                            headers=header,
                            timeout=10)
    if response.status_code == 200:
        format_result(response.json())
        return response.json()
    else:
        print(response.status_code)
        generated_error = 'There is a '
        + str(response.status_code)
        + ' error with this request'
        log_error(generated_error) 


def format_result(data):
    """Prints data in a specified format

    :param data: data fetched from API
    """

    text = json.dumps(data, indent=4)
    print(text)


def show_tasks():
    """Show tasks to choose as a Menu
    """

    config = load_from_config()
    # Get the API options from the config
    api_options = config['apiOptions']
    print(config['generalStrings']['whichApi'])
    for i, option in enumerate(api_options, start=0):
        print(f"{i}. {option}")


def get_user_choice():
    """Get user input from menu

    :returns: The user choice
    """

    config = load_from_config()
    return input(config['generalStrings']['enterChoice'])


def get_url(choice):
    """Get URL for API

    :param choice: user choice input
    :returns: URL of the API after user choice
    """

    config = load_from_config()
    access_token = get_access_token()
    content_type = config['accessToken']['headers']['Content-Type']
    header = {'Content-Type': content_type, 'Authorization': access_token}


    if choice == '0':
        url_obj = {'url': config['generalStrings']['exiting'], 'parameters': {}, 'header': header}
        return url_obj
    elif choice == '1':
        url_obj = {'url': config['apiUrls']['beaverBus'], 'parameters': {}, 'header': header}
        return url_obj
    elif choice == '2':
        url_obj = {'url': config['apiUrls']['terms'], 'parameters': {}, 'header': header}
        return url_obj
    elif choice == '3':
        user_date = input('Enter Date (yyyy-mm-dd): ')
        url_obj = {'url _terms': config['apiUrls']['terms'], 'url _textbooks': config['apiUrls']['textbooks'], 'parameters': {'date': user_date}, 'header': header}
        return url_obj
    else:
        print(config['generalStrings']['invalidChoice'])


def get_text_books_with_date(url_obj):
   
    terms_data_response = get_api_data(url_obj['url _terms'], url_obj['parameters'], url_obj['header'])
    academicYear = terms_data_response['data'][0]['attributes']['calendarYear']
    term = terms_data_response['data'][0]['attributes']['season']
    url_obj['textbooks_parameters'] = {'academicYear': academicYear, 'term': term, 'subject': 'CS', 'courseNumber': '161'}
    #textbooks_data_response = get_api_data(url_obj['url _textbooks'], url_obj['textbooks_parameters'], url_obj['header'])


if __name__ == '__main__':
    """Driver function
    """

    while True:
        show_tasks()
        user_choice = get_user_choice()
        url_obj = get_url(user_choice)
        if user_choice == '0':
            print(url_obj['url'])
            break
        if (
            user_choice == '1'
            or user_choice == '2'
        ):
            api_call = get_api_data(url_obj['url'], url_obj['parameters'], url_obj['header'])
        elif user_choice == '3':
            api_call = get_text_books_with_date(url_obj)
