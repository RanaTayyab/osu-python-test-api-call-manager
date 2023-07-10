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
    formatted_message = f'[{current_time}] {error_message}'

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

    response = requests.get(f'{url}',
                            params=parameters,
                            headers=header,
                            timeout=10)
    if response.status_code == 200:
        # format_result(response.json())
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
        print(f'{i}. {option}')


def get_user_choice():
    """Get user input from menu

    :returns: The user choice
    """

    config = load_from_config()
    return input(config['generalStrings']['enterChoice'])


def get_url(choice):
    """Get URL for API

    :param choice: user choice input
    :returns: API URL Object after user choice
    """

    config = load_from_config()
    access_token = get_access_token()
    content_type = config['accessToken']['headers']['Content-Type']
    header = {'Content-Type': content_type, 'Authorization': access_token}
    url_obj = {}
    if choice == '0':
        url_obj = {'url': config['generalStrings']['exiting'],
                   'parameters': {},
                   'header': header}
    elif choice == '1':
        url_obj = {'url': config['apiUrls']['beaverBus'],
                   'parameters': {},
                   'header': header}
    elif choice == '2':
        url_obj = {'url': config['apiUrls']['terms'],
                   'parameters': {},
                   'header': header}
    elif choice == '3':
        user_date = input('Enter Date (yyyy-mm-dd): ')
        url_obj = {'url_terms': config['apiUrls']['terms'],
                   'url_textbooks': config['apiUrls']['textbooks'],
                   'parameters': {'date': user_date},
                   'header': header}
    elif choice == '4':
        route_id = input('Enter Route Number: ')
        url_obj = {'url_routes': config['apiUrls']['routes'],
                   'url_arrivals': config['apiUrls']['arrivals'],
                   'url_vehicles': config['apiUrls']['vehicles'],
                   'route_id': route_id,  'parameters': {},
                   'header': header}
    else:
        print(config['generalStrings']['invalidChoice'])

    return url_obj


def get_text_books_with_term_date(url_obj):
    """Get text books based on specified term and date
    """

    terms_data_response = get_api_data(url_obj['url_terms'],
                                       url_obj['parameters'],
                                       url_obj['header'])
    academic_year = terms_data_response['data'][0]['attributes']['calendarYear']
    term = terms_data_response['data'][0]['attributes']['season']
    url_obj['textbooks_parameters'] = {'academicYear': academic_year,
                                       'term': term,
                                       'subject': 'CS',
                                       'courseNumber': '161'}


def get_stops_vehicles_on_route(url_obj):
    """Get stops and vehicles on a given route
    and determine where it is heading in real time
    and the ETA for the stop
    """

    routes_data_response = get_api_data(url_obj['url_routes']+'/'+url_obj['route_id'],
                                        url_obj['parameters'],
                                        url_obj['header'])
    route_name = routes_data_response['data']['attributes']['description']
    stops = routes_data_response['data']['attributes']['stops']

    for stop in stops:
        stop_id = stop['stopID']
        description = stop['description']
        url_obj['parameters'] = {'stopID': stop_id, 'routeID': url_obj['route_id']}
        arrivals_data_response = get_api_data(url_obj['url_arrivals'],
                                              url_obj['parameters'],
                                              url_obj['header'])
        get_vehicle_id = arrivals_data_response['data'][0]['attributes']['arrivals'][0]['vehicleID']
        get_eta_at_Stop = arrivals_data_response['data'][0]['attributes']['arrivals'][0]['eta']
        vehicles_data_response = get_api_data(url_obj['url_vehicles']+'/'+get_vehicle_id,
                                              {},
                                              url_obj['header'])
        get_vehicle_name = vehicles_data_response['data']['attributes']['name']
        get_vehicle_heading = vehicles_data_response['data']['attributes']['heading']

        print(f"Route ID: {url_obj['route_id']}, Route Name: {route_name}, Stop ID: {stop_id}, Stop Name: {description}, Vehicle Name: {get_vehicle_name}  , Vehicle Number: {get_vehicle_id}, Heading: {get_vehicle_heading}, ETA for arrival to Stop: {get_eta_at_Stop}")


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
            api_call = get_text_books_with_term_date(url_obj)
        elif user_choice == '4':
            api_call = get_stops_vehicles_on_route(url_obj)
