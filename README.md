# API Manager

The API Manager is a Python class that allows you to interact with various Public OSU APIs and perform different operations based on user input. It provides functionalities to retrieve access tokens, make public API requests, log errors, and display menu options for the user to choose from, such as:

* Beaver Bus
* Terms API
* Textbooks API
* Beaver Bus Routes API
* Beaver Bus Arrivals API
* Vehicles API

## Installation

To use the API Manager, you need to have Python installed on your system. You can download Python from the official website: [Python.org](https://www.python.org/)

## Setup

1. Clone or download the project repository to your local machine.
2. Install the required dependencies by running the following command:

```python
pip install -r requirements.txt
```

3. Create a `configuration.yaml` file in the project directory and populate it with the required configuration parameters. See the "Configuration" section below for details.

## Configuration

The `configuration.yaml` file contains important parameters for the API Manager. It should have the following structure:

```yaml
access_token:
  url: https://api.example.com/oauth2/token
  payload:
    client_id: client_id
    client_secret: client_secret
apiUrls:
  beaver_bus: https://api.example.com/v1/beaverbus
  terms: https://api.example.com/v1/terms
  textbooks: https://api.example.com/v1/textbooks
  routes: https://api.example.com/v1/routes
  arrivals: https://api.example.com/v1/arrivals
  vehicles: https://api.example.com/v1/vehicles
```

4. Replace the example URLs and credentials with the actual values specific to the APIs you are working with.

## Usage

5. To use the API Manager, follow these steps:

    * Create an instance of the `ApiManager` class:

    ```python
    api_manager = ApiManager()
    ```

    * Call the `main` method to start the application:

    ```python
    api_manager.main()
    ```

6. The application will display a menu with different API options. Enter the corresponding number to choose an option.

7. Follow the prompts or provide input as required by the chosen API option.

8. The application will retrieve and display the requested data or perform the specified operation based on the selected API option.

9. Continue using the application until you choose to exit.

## Logging

The API Manager provides two logging methods: `log_error` and `log_message`. These methods log messages with date and time information in PST (America/Los_Angeles timezone).

* To log a message, use the `log_message` method:

```python
api_manager.log_message("This is a general log message")
```
Log messages will be appended to the logfile.log file in the project directory.

## Contributing

Contributions to the API Manager project are welcome. If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository: API Manager

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
