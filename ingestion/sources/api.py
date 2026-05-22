import logging
import requests

logger = logging.getLogger(__name__)


def fetch_data_from_api(url, params=None, headers=None, timeout=10):
    try:
        response = requests.get(
            url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching data from API: {e}")
        raise


class APIClient:
    def __init__(self, base_url, timeout):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()

    def _build_url(self, endpoint):
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def get(self, endpoint, params=None, headers=None):
        try:
            url = self._build_url(endpoint)

            response = self.session.get(
                url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Request timed out for {self.url}")
            raise
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for {self.url}")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"HTTP error {e.response.status_code}: {e.response.text} for {self.url}")
            raise
        except requests.RequestException as e:
            logger.error(f"Error fetching data from {self.url}: {e}")
            raise
