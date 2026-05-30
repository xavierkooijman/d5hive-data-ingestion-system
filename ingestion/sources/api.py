import logging
import requests

logger = logging.getLogger(__name__)


class APIClient:
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()

    def _build_url(self, endpoint: str) -> str:
        """Construct the full URL for the API request.
        Args:
            endpoint (str): The API endpoint to append to the base URL.
        Returns:
            str: The full API URL.
        """
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def get(self, endpoint: str, params: dict = None, headers: dict = None) -> dict:
        """Make a GET request to the specified API endpoint.
        Args:
            endpoint (str): The API endpoint to request.
            params (dict, optional): Query parameters for the request.
            headers (dict, optional): Headers for the request.
        Returns:
            dict: The JSON response from the API or an error message.
        """
        try:
            url = self._build_url(endpoint)

            logger.info(
                f"Making GET request to {url} with params: {params} and headers: {headers}")

            response = self.session.get(
                url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            logger.info(
                f"GET request to {url} successful with status code {response.status_code}")
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Request timed out for {url}")
            raise
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for {url}")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"HTTP error {e.response.status_code}: {e.response.text} for {url}")
            raise
        except requests.RequestException as e:
            logger.error(f"Error fetching data from {url}: {e}")
            raise
