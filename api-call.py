import datetime
import json
import logging
from typing import Dict, Any, Union

import pytz
import requests
import yaml


class ApiManager:
    def __init__(self):
        self.config = self.load_from_config()

    def load_from_config(self) -> Any:
        """Loading important parameters from configuration file

        :returns: The config object
        """

        with open('configuration.yaml', 'r') as file:
            return yaml.safe_load(file)

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
            file.write(formatted_message + '\n')

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
        headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}

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

    def get_api_data(self, url: str, parameters: Dict[str, Any], header: Dict[str, str]) -> Any:
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

    def format_result(self, response: requests.Response) -> Any:
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

    def get_url(self, choice: str) -> Dict[str, Any]:
        """Get URL for API

        :param choice: user choice input
        :returns: API URL Object after user choice
        """

        access_token = self.get_access_token()
        header = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8', 'Authorization': access_token}
        url_obj = {}
        if choice == '0':
            return 'Exiting...'
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
                    'url_textbooks': self.config['api_urls']['textbooks'],
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

    def get_text_books_with_term_date(self, url_obj: Dict[str, Any]) -> None:
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
                    if calendar_year is None:
                        print("Error: 'calendarYear' attribute is missing or empty")
                    if season is None:
                        print("Error: 'season' attribute is missing or empty")
                else:
                    print("Error: 'attributes' key is missing in the first term object")
            else:
                print("Error: 'data' key is missing or empty")

    def get_stops_vehicles_on_route(self, url_obj: Dict[str, Any]) -> None:
        """Get stops and vehicles on a given route
        and determine where it is heading in real time
        and the ETA for the stop
        """

        routes_data_response = self.get_api_data(
            f"{url_obj['url_routes']}/{url_obj['route_id']}",
            url_obj['parameters'],
            url_obj['header']
        )
        if routes_data_response:
            if 'data' in routes_data_response:
                route_data = routes_data_response['data']

                if 'attributes' in route_data:
                    route_attributes = route_data['attributes']

                    if 'description' in route_attributes:
                        route_name = route_attributes['description']
                    else:
                        print("Error: 'description' key is missing in route attributes")
                else:
                    print("Error: 'attributes' key is missing in route data")
            else:
                print("Error: 'data' key is missing in routes data")

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
                    if arrivals_data_response:

                        if 'data' in arrivals_data_response:
                            arrivals_data = arrivals_data_response['data']

                            if arrivals_data and 'attributes' in arrivals_data[0]:
                                arrivals_attributes = arrivals_data[0]['attributes']

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
                                        if vehicles_data_response:

                                            if 'data' in vehicles_data_response:
                                                vehicles_data = vehicles_data_response['data']

                                                if 'attributes' in vehicles_data:
                                                    vehicles_attributes = vehicles_data['attributes']

                                                    if 'name' in vehicles_attributes and 'heading' in vehicles_attributes:
                                                        get_vehicle_name = vehicles_attributes['name']
                                                        get_vehicle_heading = vehicles_attributes['heading']

                                                    else:
                                                        print("Error: 'name' or 'heading' key is missing in vehicles attributes")
                                                else:
                                                    print("Error: 'attributes' key is missing in vehicles data")
                                            else:
                                                print("Error: 'data' key is missing in vehicles data response")
                                        else:
                                            print("Error: 'vehicleID' or 'eta' key is missing in the first arrival object")
                                    else:
                                        print("Error: 'arrivals' key is missing or empty in arrivals attributes")
                                else:
                                    print("Error: 'attributes' key is missing or empty in the first arrivals data")
                            else:
                                print("Error: 'data' key is missing in arrivals data response")
                        else:
                            print("Error: 'stopID' or 'description' key is missing in stop object")

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
