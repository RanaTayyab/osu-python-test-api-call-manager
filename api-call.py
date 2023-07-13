import datetime
import json
import logging
from typing import Dict, Union

import pytz
import requests
import yaml


class ApiManager:
    def __init__(self):
        print("Started the process and validating 'configuration.yaml' file.")
        validation = self.validate_config('configuration.yaml')
        if validation:
            self.config = self.load_from_config()
        else:
            print("'configuration.yaml' file is not correct.")
            exit()

    def load_from_config(self) -> Dict:
        """Loading important parameters from configuration file

        :returns: The config object
        """

        with open('configuration.yaml', 'r') as file:
            return yaml.safe_load(file)
        
    def validate_config(self, config_path: str) -> bool:
        """Validate the config.yaml file and verify the URLs.

        :param config_path: The path to the config.yaml file.
        :return: True if the config and URLs are valid, False otherwise.
        """
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Error: Config file '{config_path}' not found.")
            return False
        except yaml.YAMLError:
            print(f"Error: Invalid YAML syntax in '{config_path}'.")
            return False

        # Verify access_token URL
        access_token_url = config.get('access_token', {}).get('url')
        access_token_payload = config.get('access_token', {}).get('payload', {})
        access_token_payload['grant_type'] = 'client_credentials'
        access_token_header = {'Content-Type': 'application/x-www-form-urlencoded'}
        token = self.verify_url_token(access_token_url, access_token_header, access_token_payload)
        if 'Bearer' not in token:
            print(f'Error: Invalid access_token URL: {access_token_url}')
            return False

        # Verify API URLs
        api_urls = config.get('api_urls', {})
        header = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': token}
        for name, url in api_urls.items():
            if not self.verify_urls(url, header):
                print(f"Error: Invalid API URL '{name}': {url}")
                return False

        # All checks passed, config is valid
        return True

    def verify_urls(self, url: str, header: Dict[str, str]) -> bool:
        """Verify the correctness and functionality of a URL.

        :param url: The URL to verify.
        :param header: The header to send with the request.
        :return: True if the URL is valid and functional, False otherwise.
        """
        try:
            response = requests.head(url, headers=header)
            return response.status_code == requests.codes.ok
        except requests.exceptions.RequestException:
            return False

    def verify_url_token(self, url: str, header: Dict[str, str], data: Dict[str, str] = None) -> str:
        """Verify the correctness and functionality of a URL.

        :param url: The URL to verify.
        :param header: The header to send with the request.
        :param data: The data to include in the request payload (optional).
        :return: Token otherwise empty string.
        """
        try:
            response = requests.post(url, headers=header, data=data)
            access_token = response.json()['access_token']
            return f'Bearer {access_token}'
        except requests.exceptions.RequestException:
            return ''

    def log_error(self, error_message: str) -> None:
        """Logging any error messages in the file and appending
        with date time information in PST

        :param error_message: The error message to log in file as a string
        :return: None
        """

        # Get the current datetime in PST
        pst_timezone = pytz.timezone('America/Los_Angeles')
        current_time = datetime.datetime.now(pst_timezone)
        formatted_message = f'[{current_time}] {error_message}'

        # Append the error message to the logfile
        with open('logfile.txt', 'a') as file:
            file.write(f'{formatted_message}\n')

    def log_message(self, message: str) -> None:
        """Logging any messages in the logfile.log
        with date time information in PST

        :param message: The message to log in file
        :return: None
        """
        pst_timezone = pytz.timezone('America/Los_Angeles')
        current_time = datetime.datetime.now(pst_timezone)

        # Configure the logger
        logging.basicConfig(
            filename='logfile.log',
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S %Z'
        )

        logging.info(f'{current_time}: {message}')

    def get_access_token(self) -> str:
        """Get access token from OAuth2 for connecting with OSU public APIs

        :returns: The access token string
        """
        url = self.config['access_token']['url']
        payload = self.config['access_token']['payload']
        payload['grant_type'] = 'client_credentials'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(
            url,
            data=payload,
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            access_token = response.json()['access_token']
            return f'Bearer {access_token}'
        else:
            self.log_message(f'Request failed with status code: {response.status_code}')
            print(f'{response.status_code}: {self.get_http_status_description(response.status_code)}')
            return ''

    def get_api_data(self, url: str, parameters: Dict[str, str], header: Dict[str, str]) -> Dict:
        """Get Request for getting the data from API

        :param url: URL of the API
        :param parameters: The parameters for API
        :param header: The headers for API with authorization
        :return: The response data from the API
        """

        response = requests.get(
            url,
            params=parameters,
            headers=header,
            timeout=10
        )
        if response.status_code == 200:
            return self.format_result(response)
        else:
            print(f'{response.status_code}: {self.get_http_status_description(response.status_code)}')
            self.log_message(f'{response.status_code}: {self.get_http_status_description(response.status_code)}')

    def format_result(self, response: requests.Response) -> Dict:
        """Returns data from response object after JSON validation

        :param response: The API response object
        :return: The validated data
        """
        try:
            data = response.json()
        except json.decoder.JSONDecodeError:
            print("Invalid JSON response")

        text = json.dumps(data, indent=4)
        return data
    
    def get_http_status_description(self, status_code: int) -> Union[str, None]:
        """Get the description of an HTTP status code.

        :param status_code: The HTTP status code to get the description for.
        :return: The description of the HTTP status code, or None if the status code is not recognized.
        """

        status_descriptions: Dict[int, str] = {
            200: 'OK - The request has succeeded.',
            400: 'Bad Request - The server could not understand the request due to invalid syntax or missing parameters.',
            401: 'Unauthorized - The request requires user authentication or authentication failed.',
            403: 'Forbidden - The server understood the request but refuses to authorize it.',
            404: 'Not Found - The requested resource could not be found.',
            500: 'Internal Server Error - The server encountered an unexpected condition that prevented it from fulfilling the request.',
            502: 'Bad Gateway - The server received an invalid response from an upstream server.',
            503: 'Service Unavailable - The server is currently unable to handle the request due to a temporary overload or maintenance.',
            504: 'Gateway Timeout - The server did not receive a timely response from an upstream server.',
            505: 'HTTP Version Not Supported - The server does not support the HTTP protocol version used in the request.'
        }

        return status_descriptions.get(status_code)

    def show_tasks(self) -> None:
        """Show tasks to choose as a Menu
        """
        api_options = ['Quit',
                    'Beavers Bus',
                    'Terms',
                    'Search Text Books of a Term by a custom/any Date',
                    'Get Details of a Vehicle and its Stops given a specified Route, with ETA and current destination']
        
        print('Which API data do you want to check?')
        for i, option in enumerate(api_options):
            print(f'{i}. {option}')

    def get_user_choice(self) -> str:
        """Get user input from menu

        :returns: The user choice
        """
        return input('Enter your choice (0 or 1 or 2 or 3 or 4): ')

    def get_url(self, choice: str) -> Dict[str, str]:
        """Get URL for API

        :param choice: user choice input
        :returns: API URL Object after user choice
        """

        access_token = self.get_access_token()
        if 'Bearer' not in access_token:
            print(f'Error: Invalid access_token of the application, could not connect')
            exit()
        header = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': access_token}
        url_obj = {}
        if choice == '0':
            return 'Exit'
        elif choice == '1':
            url_obj = {'url': self.config['api_urls']['beaver_bus'],
                    'parameters': {},
                    'header': header}
        elif choice == '2':
            url_obj = {'url': self.config['api_urls']['terms'],
                    'parameters': {},
                    'header': header}
        elif choice == '3':
            user_date = input('Enter Date (yyyy-mm-dd): ')
            url_obj = {'url_terms': self.config['api_urls']['terms'],
                    'parameters': {'date': user_date},
                    'header': header}
        elif choice == '4':
            route_id = input('Enter Route Number: ')
            url_obj = {'url_routes': self.config['api_urls']['routes'],
                    'url_arrivals': self.config['api_urls']['arrivals'],
                    'url_vehicles': self.config['api_urls']['vehicles'],
                    'route_id': route_id,  'parameters': {},
                    'header': header}
        else:
            print('Invalid choice. Please try again.')

        return url_obj

    def get_text_books_with_term_date(self, url_obj: Dict[str, str]) -> None:
        """Get text books based on specified term and date
        """

        terms_data_response = self.get_api_data(
            url_obj['url_terms'],
            url_obj['parameters'],
            url_obj['header']
        )
        if terms_data_response:
            terms_data = terms_data_response.get('data', [])
            if terms_data:
                first_term = terms_data[0]
                if 'attributes' in first_term:
                    attributes = first_term['attributes']
                    calendar_year = attributes.get('calendarYear')
                    season = attributes.get('season')
                    if not calendar_year:
                        print("Error: 'calendarYear' attribute is missing or empty")
                    if season is None:
                        print("Error: 'season' attribute is missing or empty")
                else:
                    print("Error: 'attributes' key is missing in the first term object")
            else:
                print("Error: 'data' key is missing or empty, Check your query again for these parameters")


    def validate_data_response(self, data_response: Dict[str, Dict]) -> Union[Dict, bool]:
        """Validates the data_response dictionary for required keys and values.

        :param data_response: The dictionary to validate
        :return: attributes if the validation passes, False otherwise
        """
        if data_response:
            if 'data' in data_response:
                data = data_response['data']

                if 'attributes' in data:
                    return data['attributes']
                elif 'attributes' in data[0]:
                    return data[0]['attributes']
                else:
                    print("Error: 'attributes' key is missing in data")
            else:
                print("Error: 'data' key is missing in data_response, Check your query again for these parameters")
        else:
            print("Error: Empty data_response")

        return False


    def get_stops_vehicles_on_route(self, url_obj: Dict[str, str]) -> None:
        """Get stops and vehicles on a given route
        and determine where it is heading in real time
        and the ETA for the stop
        """

        routes_data_response = self.get_api_data(
            f"{url_obj['url_routes']}/{url_obj['route_id']}",
            url_obj['parameters'],
            url_obj['header']
        )
        route_attributes = self.validate_data_response(routes_data_response)
        if 'description' in route_attributes:
            route_name = route_attributes['description']
        else:
            print("Error: 'description' key is missing in route attributes")

        stops = route_attributes.get('stops', [])
        for stop in stops:
            if 'stopID' in stop and 'description' in stop:
                stop_id = stop['stopID']
                description = stop['description']

                url_obj['parameters'] = {'stopID': stop_id, 'routeID': url_obj['route_id']}
                arrivals_data_response = self.get_api_data(
                    url_obj['url_arrivals'],
                    url_obj['parameters'],
                    url_obj['header']
                )
                arrivals_attributes = self.validate_data_response(arrivals_data_response)
                if 'arrivals' in arrivals_attributes and arrivals_attributes['arrivals']:
                    first_arrival = arrivals_attributes['arrivals'][0]

                    if 'vehicleID' in first_arrival and 'eta' in first_arrival:
                        get_vehicle_id = first_arrival['vehicleID']
                        get_eta_at_stop = first_arrival['eta']

                        vehicles_data_response = self.get_api_data(
                            f"{url_obj['url_vehicles']}/{get_vehicle_id}",
                            {},
                            url_obj['header']
                        )
                        vehicles_attributes = self.validate_data_response(vehicles_data_response)
                        if 'name' in vehicles_attributes and 'heading' in vehicles_attributes:
                            get_vehicle_name = vehicles_attributes['name']
                            get_vehicle_heading = vehicles_attributes['heading']
                        else:
                            print("Error: 'name' or 'heading' key is missing in vehicles attributes")
                    else:
                        print("Error: 'vehicleID' or 'eta' key is missing in the first arrival object")
                else:
                    print("Error: 'arrivals' key is missing or empty in arrivals attributes")
            else:
                print("Error: 'stopID' or 'description' key is missing in stop object, Check your query again for these parameters")

            print(f"Route ID: {url_obj['route_id']}, Route Name: {route_name}, Stop ID: {stop_id}, Stop Name: {description}, Vehicle Name: {get_vehicle_name}, Vehicle Number: {get_vehicle_id}, Heading: {get_vehicle_heading}, ETA for arrival to Stop: {get_eta_at_stop}")

    def main(self) -> None:
        """Driver function of class
        """
        while True:
            self.show_tasks()
            user_choice = self.get_user_choice()
            url_obj = self.get_url(user_choice)
            if user_choice == '0':
                print(url_obj)
                break
            if (
                user_choice in ('1', '2')
            ):
                self.get_api_data(
                    url_obj['url'],
                    url_obj['parameters'],
                    url_obj['header']
                )
            elif user_choice == '3':
                self.get_text_books_with_term_date(url_obj)
            elif user_choice == '4':
                self.get_stops_vehicles_on_route(url_obj)


if __name__ == '__main__':
    api_manager = ApiManager()
    api_manager.main()
