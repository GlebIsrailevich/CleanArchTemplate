# import os

# import requests

# API_URL = os.environ.get("API_URL", "http://localhost:8000/api")


# class APIClient:
#     def __init__(self, base_url=API_URL):
#         self.base_url = base_url

#     def _send_request(self, method, path, token=None, **kwargs):
#         headers = kwargs.get("headers", {})
#         if token:
#             headers["Authorization"] = f"Bearer {token}"
#         response = requests.request(
#             method, f"{self.base_url}{path}", headers=headers, **kwargs
#         )
#         response.raise_for_status()
#         return response.json()

#     def get(self, path, token=None, **kwargs):
#         return self._send_request("GET", path, token=token, **kwargs)

#     def post(self, path, token=None, **kwargs):
#         return self._send_request("POST", path, token=token, **kwargs)


# api_client = APIClient()


# def fetch_users_report(user_session):
#     return api_client.get("/admin/users-report", token=user_session["access_token"])


# def fetch_predictions_reports(user_session):
#     return api_client.get(
#         "/admin/predictions-reports", token=user_session["access_token"]
#     )


# def fetch_credits_report(user_session):
#     return api_client.get("/admin/credits-report", token=user_session["access_token"])


# def fetch_user_balance(user_session):
#     response = api_client.get("/billing/balance", token=user_session["access_token"])
#     return response


# def deposit_amount(amount, user_session):
#     response = api_client.post(
#         "/billing/deposit",
#         token=user_session["access_token"],
#         json={"amount": amount},
#     )
#     return response


# def fetch_transaction_history(user_session):
#     response = api_client.get("/billing/history", token=user_session["access_token"])
#     return response


# def fetch_models(user_session):
#     response = api_client.get("/prediction/models", token=user_session["access_token"])
#     return response


# def fetch_prediction_history(user_session):
#     response = api_client.get("/prediction/history", token=user_session["access_token"])
#     return response


# def send_prediction_request(selected_model, json, user_session):
#     payload = {"model_name": selected_model, "features": json}
#     response = api_client.post(
#         "/prediction/make", json=payload, token=user_session["access_token"]
#     )
#     return response


# def authenticate_user(email, password):
#     try:
#         response = api_client.post(
#             "/auth/sign-in", json={"email": email, "password": password}
#         )
#         if response:
#             return response, None
#         else:
#             return None, "Authentification failed: No response from server"
#     except Exception as e:
#         return None, str(e)


# def register_user(email, password, name):
#     try:
#         response = api_client.post(
#             "/auth/sign-up",
#             json={"email": email, "password": password, "name": name},
#         )
#         if response:
#             return response, None
#         else:
#             return None, "Registration failed: No response from server"
#     except Exception as e:
#         return None, str(e)

# import logging
# import os
# from typing import Any, Dict, Optional

# import requests

# # Setup logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# API_URL = os.environ.get("API_URL", "http://localhost:8000/api")


# class APIClient:
#     def __init__(self, base_url=API_URL):
#         self.base_url = base_url

#     def _send_request(self, method, path, token=None, **kwargs):
#         headers = kwargs.get("headers", {})
#         if token:
#             headers["Authorization"] = f"Bearer {token}"

#         # Update kwargs with new headers
#         kwargs["headers"] = headers

#         try:
#             logger.info(f"Sending {method} request to {self.base_url}{path}")
#             response = requests.request(method, f"{self.base_url}{path}", **kwargs)
#             response.raise_for_status()
#             return response.json()
#         except requests.exceptions.HTTPError as http_err:
#             logger.error(
#                 f"HTTP error: {http_err}, Status code: {response.status_code}, Response: {response.text}"
#             )
#             if response.status_code == 403:
#                 # Token might be expired, handle appropriately
#                 logger.error("Authorization failed. Token might be expired or invalid.")
#             raise
#         except requests.exceptions.ConnectionError as conn_err:
#             logger.error(f"Connection error: {conn_err}")
#             raise
#         except requests.exceptions.Timeout as timeout_err:
#             logger.error(f"Timeout error: {timeout_err}")
#             raise
#         except requests.exceptions.RequestException as req_err:
#             logger.error(f"Request error: {req_err}")
#             raise
#         except Exception as e:
#             logger.error(f"Unexpected error: {e}")
#             raise

#     def get(self, path, token=None, **kwargs):
#         return self._send_request("GET", path, token=token, **kwargs)

#     def post(self, path, token=None, **kwargs):
#         return self._send_request("POST", path, token=token, **kwargs)


# api_client = APIClient()


# def fetch_users_report(user_session):
#     return api_client.get("/admin/users-report", token=user_session["access_token"])


# def fetch_predictions_reports(user_session):
#     return api_client.get(
#         "/admin/predictions-reports", token=user_session["access_token"]
#     )


# def fetch_credits_report(user_session):
#     return api_client.get("/admin/credits-report", token=user_session["access_token"])


# def fetch_user_balance(user_session: Dict[str, Any]) -> Optional[int]:
#     """
#     Fetch the user's balance with proper error handling
#     """
#     try:
#         if not user_session or not user_session.get("access_token"):
#             logger.error("No valid user session or token available")
#             return 0  # Default value if no token

#         response = api_client.get(
#             "/billing/balance", token=user_session["access_token"]
#         )
#         return response
#     except requests.exceptions.HTTPError as e:
#         if e.response.status_code == 403:
#             logger.error("Permission denied when accessing balance endpoint")
#             return 0  # Default value on authentication error
#         logger.error(f"HTTP error when fetching balance: {e}")
#         return 0
#     except Exception as e:
#         logger.error(f"Error fetching balance: {e}")
#         return 0


# def deposit_amount(amount, user_session):
#     try:
#         response = api_client.post(
#             "/billing/deposit",
#             token=user_session["access_token"],
#             json={"amount": amount},
#         )
#         return response
#     except Exception as e:
#         logger.error(f"Error depositing amount: {e}")
#         return None


# def fetch_transaction_history(user_session):
#     try:
#         response = api_client.get(
#             "/billing/history", token=user_session["access_token"]
#         )
#         return response
#     except Exception as e:
#         logger.error(f"Error fetching transaction history: {e}")
#         return []


# def fetch_models(user_session):
#     try:
#         response = api_client.get(
#             "/prediction/models", token=user_session["access_token"]
#         )
#         return response
#     except Exception as e:
#         logger.error(f"Error fetching models: {e}")
#         return []


# def fetch_prediction_history(user_session):
#     try:
#         response = api_client.get(
#             "/prediction/history", token=user_session["access_token"]
#         )
#         return response
#     except Exception as e:
#         logger.error(f"Error fetching prediction history: {e}")
#         return []


# def send_prediction_request(selected_model, json, user_session):
#     try:
#         payload = {"model_name": selected_model, "features": json}
#         response = api_client.post(
#             "/prediction/make", json=payload, token=user_session["access_token"]
#         )
#         return response
#     except Exception as e:
#         logger.error(f"Error sending prediction request: {e}")
#         return None


# def authenticate_user(email, password):
#     try:
#         response = api_client.post(
#             "/auth/sign-in", json={"email": email, "password": password}
#         )
#         if response:
#             return response, None
#         else:
#             return None, "Authentification failed: No response from server"
#     except Exception as e:
#         return None, str(e)


# def register_user(email, password, name):
#     try:
#         response = api_client.post(
#             "/auth/sign-up",
#             json={"email": email, "password": password, "name": name},
#         )
#         if response:
#             return response, None
#         else:
#             return None, "Registration failed: No response from server"
#     except Exception as e:
#         return None, str(e)

import logging
import os
from typing import Any, Dict, Optional

import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = os.environ.get("API_URL", "http://localhost:8000/api")


class APIClient:
    def __init__(self, base_url=API_URL):
        self.base_url = base_url

    def _send_request(self, method, path, token=None, **kwargs):
        headers = kwargs.get("headers", {})
        if token:
            headers["Authorization"] = f"Bearer {token}"

        # Update kwargs with new headers
        kwargs["headers"] = headers

        try:
            logger.info(f"Sending {method} request to {self.base_url}{path}")
            response = requests.request(method, f"{self.base_url}{path}", **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logger.error(
                f"HTTP error: {http_err}, Status code: {response.status_code}, Response: {response.text}"
            )
            if response.status_code == 403:
                # Token might be expired, handle appropriately
                logger.error("Authorization failed. Token might be expired or invalid.")
            raise
        except requests.exceptions.ConnectionError as conn_err:
            logger.error(f"Connection error: {conn_err}")
            raise
        except requests.exceptions.Timeout as timeout_err:
            logger.error(f"Timeout error: {timeout_err}")
            raise
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request error: {req_err}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    def get(self, path, token=None, **kwargs):
        return self._send_request("GET", path, token=token, **kwargs)

    def post(self, path, token=None, **kwargs):
        return self._send_request("POST", path, token=token, **kwargs)


api_client = APIClient()


def fetch_users_report(user_session):
    return api_client.get("/admin/users-report", token=user_session["access_token"])


def fetch_predictions_reports(user_session):
    return api_client.get(
        "/admin/predictions-reports", token=user_session["access_token"]
    )


def fetch_credits_report(user_session):
    return api_client.get("/admin/credits-report", token=user_session["access_token"])


def fetch_user_balance(user_session: Dict[str, Any]) -> Optional[int]:
    """
    Fetch the user's balance with proper error handling
    """
    try:
        if not user_session or not user_session.get("access_token"):
            logger.error("No valid user session or token available")
            return 0  # Default value if no token

        response = api_client.get(
            "/billing/balance", token=user_session["access_token"]
        )
        return response
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            logger.error("Permission denied when accessing balance endpoint")
            return 0  # Default value on authentication error
        logger.error(f"HTTP error when fetching balance: {e}")
        return 0
    except Exception as e:
        logger.error(f"Error fetching balance: {e}")
        return 0


def _send_request(self, method, path, token=None, **kwargs):
    headers = kwargs.get("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # Add validation
    if not token and path not in ["/auth/sign-in", "/auth/sign-up"]:
        logger.error("No token for protected route: %s", path)
        raise PermissionError("Authentication required")


def deposit_amount(amount, user_session):
    try:
        response = api_client.post(
            "/billing/deposit",
            token=user_session["access_token"],
            json={"amount": amount},
        )
        return response
    except Exception as e:
        logger.error(f"Error depositing amount: {e}")
        return None


def fetch_transaction_history(user_session):
    try:
        response = api_client.get(
            "/billing/history", token=user_session["access_token"]
        )
        return response
    except Exception as e:
        logger.error(f"Error fetching transaction history: {e}")
        return []


# def fetch_models(user_session):
#     try:
#         if not user_session or not user_session.get("access_token"):
#             logger.error(
#                 "No valid user session or token available when fetching models"
#             )
#             return []  # Return empty list if no token

#         response = api_client.get(
#             "/prediction/models", token=user_session["access_token"]
#         )

#         # Check if the response is valid
#         if not response or not isinstance(response, list):
#             logger.warning(f"Unexpected model response format: {response}")
#             return []

#         return response
#     except requests.exceptions.HTTPError as e:
#         if e.response.status_code == 403:
#             logger.error("Permission denied when accessing models endpoint")
#         else:
#             logger.error(f"HTTP error when fetching models: {e}")
#         return []
#     except Exception as e:
#         logger.error(f"Error fetching models: {e}")
#         return []


def fetch_models(user_session):
    try:
        response = api_client.get(
            "/prediction/models", token=user_session["access_token"]
        )

        # Add validation
        if not isinstance(response, list):
            logger.error("Invalid models response format")
            return []

        return [
            {
                "id": str(m.get("id")),
                "name": m.get("name", "Unnamed Model"),
                "cost": m.get(
                    "cost_per_prediction", 0
                ),  # Or "cost" depending on backend
                "description": m.get("description", ""),
            }
            for m in response
        ]

    except Exception as e:
        logger.error(f"Model processing failed: {str(e)}")
        return []


def fetch_prediction_history(user_session):
    try:
        response = api_client.get(
            "/prediction/history", token=user_session["access_token"]
        )
        return response
    except Exception as e:
        logger.error(f"Error fetching prediction history: {e}")
        return []


# def send_prediction_request(selected_model, json, user_session):
#     try:
#         payload = {"model_name": selected_model, "features": json}
#         response = api_client.post(
#             "/prediction/make", json=payload, token=user_session["access_token"]
#         )
#         return response
#     except Exception as e:
#         logger.error(f"Error sending prediction request: {e}")
#         return None


# def send_prediction_request(selected_model, json_data, user_session):
#     try:
#         # Add debug print to verify token exists
#         print(f"DEBUG - User session token: {user_session.get('access_token')}")

#         payload = {
#             "model_name": selected_model,
#             "features": json_data,  # Ensure this matches PredictionRequest schema
#         }


#         response = api_client.post(
#             "/prediction/make",
#             json=payload,
#             token=user_session.get("access_token"),  # Use .get() for safety
#         )
#         return response
#     except Exception as e:
#         logger.error(f"Prediction request failed: {str(e)}")
#         return None
# def send_prediction_request(prediction_request, user_session=None):
#     """
#     Sends a prediction request to the backend API.

#     Args:
#         prediction_request (dict): The prediction request data
#         user_session (dict): User session information including access token

#     Returns:
#         dict: Prediction results or None if there was an error
#     """
#     import requests

#     from frontend.logger import LOGGER

#     if not user_session or not user_session.get("access_token"):
#         LOGGER.error("No valid user session or token available")
#         return None

#     try:
#         headers = {
#             "Authorization": f"Bearer {user_session['access_token']}",
#             "Content-Type": "application/json",
#         }

#         # Make the API request to the backend
#         response = requests.post(
#             "http://backend:80/api/prediction/make",
#             json=prediction_request,
#             headers=headers,
#         )

#         # Check if the request was successful
#         if response.status_code == 200:
#             return response.json()
#         else:
#             LOGGER.error(
#                 f"HTTP error: {response.status_code} {response.reason} for url: {response.url}, Status code: {response.status_code}, Response: {response.text}"
#             )
#             return None

#     except Exception as e:
#         LOGGER.error(f"Error sending prediction request: {str(e)}")
#         return None


def send_prediction_request(model_name, features, user_session=None):
    """
    Sends a prediction request to the backend API.

    Args:
        model_name (str): The name of the model to use for prediction
        features (list): List of feature dictionaries for prediction
        user_session (dict): User session information including access token

    Returns:
        dict: Prediction results or None if there was an error
    """
    # Create the prediction request structure
    prediction_request = {"model_name": model_name, "features": features}
    import requests

    # from frontend.logger import LOGGER

    if not user_session or not user_session.get("access_token"):
        print("No valid user session or token available")
        return None

    try:
        headers = {
            "Authorization": f"Bearer {user_session['access_token']}",
            "Content-Type": "application/json",
        }

        # Make the API request to the backend
        response = requests.post(
            "http://backend:80/api/prediction/make",
            json=prediction_request,
            headers=headers,
        )

        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        else:
            print(
                f"HTTP error: {response.status_code} {response.reason} for url: {response.url}, Status code: {response.status_code}, Response: {response.text}"
            )
            return None

    except Exception as e:
        print(f"Error sending prediction request: {str(e)}")
        return None


def authenticate_user(email, password):
    try:
        response = api_client.post(
            "/auth/sign-in", json={"email": email, "password": password}
        )
        if response:
            return response, None
        else:
            return None, "Authentification failed: No response from server"
    except Exception as e:
        return None, str(e)


def register_user(email, password, name):
    try:
        response = api_client.post(
            "/auth/sign-up",
            json={"email": email, "password": password, "name": name},
        )
        if response:
            return response, None
        else:
            return None, "Registration failed: No response from server"
    except Exception as e:
        return None, str(e)


def sign_out(token):
    response = api_client.post("/api/auth/sign-out", token=token)
    response.raise_for_status()
    return response.json()
