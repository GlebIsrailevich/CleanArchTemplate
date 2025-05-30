import base64
import io
import json
from datetime import datetime
from json import JSONDecodeError, loads

import pandas as pd
from dash import ALL, Input, Output, State, callback_context, dcc, html
from dash.exceptions import PreventUpdate

from frontend.data.local_data import authentificated_session
from frontend.data.remote_data import (
    authenticate_user,
    deposit_amount,
    fetch_credits_report,
    fetch_models,
    fetch_prediction_history,
    fetch_predictions_reports,
    fetch_transaction_history,
    fetch_user_balance,
    fetch_users_report,
    register_user,
    send_prediction_request,
)
from frontend.layouts.admin_layout import (
    admin_layout,
    credits_report,
    predictions_report,
    users_report,
)
from frontend.layouts.billing_layout import billing_layout, transaction_history_table
from frontend.layouts.prediction_layout import (
    estimated_cost,
    prediction_history_table,
    prediction_layout,
)
from frontend.layouts.sign_in_layout import sign_in_layout
from frontend.layouts.sign_up_layout import sign_up_layout
from frontend.ui_kit.components.error_message import error_message
from frontend.ui_kit.components.navigation import navigation_bar
from frontend.ui_kit.components.user_balance import user_balance

sign_page_last_click_timestamp = datetime.now()  # to prevent changing page on update


def parse_contents(contents):
    content_type, content_string = contents[0].split(",")
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
    json_list = loads(df.to_json(orient="records"))
    return json_list


def register_callbacks(_app):
    @_app.callback(
        Output("user-session", "data"),
        [
            Input("sign-in-session-update", "data"),
            Input("sign-up-session-update", "data"),
        ],
        State("user-session", "data"),
    )
    def manage_session(sign_in_data, sign_up_data, current_session):
        ctx = callback_context

        if not ctx.triggered:
            return current_session
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if trigger_id == "sign-in-session-update" and sign_in_data:
            return sign_in_data
        elif trigger_id == "sign-up-session-update" and sign_up_data:
            return sign_up_data

        return current_session

    @_app.callback(
        Output("url", "pathname"),
        [
            Input({"type": "nav-button", "index": ALL}, "n_clicks_timestamp"),
            Input("user-session", "data"),
        ],
        State("url", "pathname"),
        prevent_initial_call=True,
    )
    def manage_navigation(n_clicks_timestamp, user_session, pathname):
        global sign_page_last_click_timestamp
        ctx = callback_context

        if (
            user_session
            and user_session.get("is_authenticated", False)
            and pathname in ["/sign-in", "/sign-up"]
        ):
            return "/prediction"
        else:
            if not ctx.triggered:
                raise PreventUpdate

            button_id = ctx.triggered[0]["prop_id"].split(".")[0]

            if not button_id:
                raise PreventUpdate

            try:
                button_index = json.loads(button_id.replace("'", '"'))["index"]
            except JSONDecodeError:
                raise PreventUpdate

            # FIX: Filter out None values before using max()
            valid_timestamps = [ts for ts in n_clicks_timestamp if ts is not None]
            click_timestamp = max(valid_timestamps) if valid_timestamps else None

            if (
                click_timestamp
                and (datetime.now() - sign_page_last_click_timestamp).total_seconds()
                > 1
            ):
                sign_page_last_click_timestamp = datetime.now()
                # if button_index == "sign-up":
                #     return "/sign-up"
                # elif button_index == "sign-in":
                #     return "/sign-in"
                if button_index == "sign-up":
                    return "/sign-up"
                elif button_index == "sign-in":
                    return "/sign-in"
                elif button_index == "sign-out":
                    return "/sign-in"
            else:
                raise PreventUpdate

    @_app.callback(
        Output("page-content", "children"),
        [Input("url", "pathname")],
        [State("user-session", "data")],
    )
    def manage_page_content(pathname, user_session):
        if user_session and user_session.get("is_authenticated"):
            if pathname == "/prediction":
                try:
                    return prediction_layout(user_session)
                except Exception as e:
                    return error_message(f"Error loading prediction page: {str(e)}")
            elif pathname == "/billing":
                try:
                    return billing_layout(user_session)
                except Exception as e:
                    return error_message(f"Error loading billing page: {str(e)}")
            elif pathname == "/admin":
                if user_session.get("is_superuser"):
                    return admin_layout()
                else:
                    return "403 Access Denied"
            else:
                return "404 Page Not Found"
        else:
            if pathname == "/sign-in":
                return sign_in_layout()
            elif pathname == "/sign-up":
                return sign_up_layout()
            else:
                return dcc.Location(id="url", href="/sign-in", refresh=True)

    @_app.callback(Output("nav-bar", "children"), [Input("user-session", "data")])
    def manage_navigation_bar(user_session):
        if user_session and user_session.get("is_authenticated"):
            return navigation_bar(user_session)
        return ""

    @_app.callback(
        [
            Output("sign-in-session-update", "data"),
            Output("sign-in-status", "children"),
        ],
        [
            Input({"type": "auth-button", "action": "sign-in"}, "n_clicks"),
        ],
        [
            State("user-session", "data"),
            State("sign-in-email", "value"),
            State("sign-in-password", "value"),
        ],
        prevent_initial_call=True,
    )
    def sign_in_callback(sign_in_clicks, _, sign_in_email, sign_in_password):
        if sign_in_clicks > 0:
            user_data, error = authenticate_user(sign_in_email, sign_in_password)
            if user_data:
                new_user_session = authentificated_session(user_data)
                return new_user_session, "Sign in successful"
            return None, error_message(error if error else "Invalid credentials")
        raise PreventUpdate

    @_app.callback(
        [
            Output("sign-up-session-update", "data"),
            Output("sign-up-status", "children"),
        ],
        [
            Input({"type": "auth-button", "action": "sign-up"}, "n_clicks"),
        ],
        [
            State("user-session", "data"),
            State("sign-up-email", "value"),
            State("sign-up-password", "value"),
            State("sign-up-name", "value"),
        ],
        prevent_initial_call=True,
    )
    def sign_up_callback(
        sign_up_clicks, _, sign_up_email, sign_up_password, sign_up_name
    ):
        if sign_up_clicks > 0:
            user_data, error = register_user(
                sign_up_email, sign_up_password, sign_up_name
            )
            if user_data:
                new_user_session = authentificated_session(user_data)
                return new_user_session, "Registration successful"

            return {}, error_message(error if error else "Registration failed")

        raise PreventUpdate

    # @_app.callback(
    #     Output("prediction-results", "children"),
    #     Input("upload-data", "contents"),
    #     State("model-dropdown", "value"),
    #     State("user-session", "data"),
    # )
    # def handle_file_upload(contents, selected_model, user_session):
    #     if not user_session or not user_session.get("access_token"):
    #         return error_message("Authentication required")  # Explicit check

    @_app.callback(
        Output("prediction-results", "children"),
        Input("upload-data", "contents"),
        [
            State("model-dropdown", "value"),
            State("user-session", "data"),
        ],
        prevent_initial_call=True,
    )
    def handle_file_upload(contents, selected_model, user_session):
        if not contents:
            raise PreventUpdate

        if not user_session or not user_session.get("access_token"):
            return error_message("Authentication required. Please sign in again.")

        if not selected_model:
            return error_message("Please select a model for prediction.")

        try:
            # Parse the uploaded CSV file
            json_features = parse_contents(contents)

            # Send the prediction request to the backend
            prediction_results = send_prediction_request(
                selected_model, json_features, user_session=user_session
            )

            if prediction_results:
                # Return results in a formatted table
                return html.Div(
                    [
                        html.H4("Prediction Results"),
                        html.Div(
                            f"Total cost: {prediction_results.get('cost', 'N/A')}"
                        ),
                        html.Table(
                            # Header
                            [html.Tr([html.Th("Features"), html.Th("Prediction")])]
                            +
                            # Rows for each prediction
                            [
                                html.Tr(
                                    [
                                        html.Td(str(pred.get("features", {}))),
                                        html.Td(
                                            str(
                                                pred.get("target", {}).get(
                                                    "answer", "N/A"
                                                )
                                            )
                                        ),
                                    ]
                                )
                                for pred in prediction_results.get("predictions", [])
                            ],
                            className="prediction-results-table",
                        ),
                    ]
                )
            else:
                return error_message(
                    "Failed to get prediction results. Please check your authentication and try again."
                )

        except Exception as e:
            return error_message(f"Error processing file: {str(e)}")

    @_app.callback(
        [
            Output("users-report-div", "children"),
            Output("predictions-report-div", "children"),
            Output("credits-report-div", "children"),
        ],
        [Input("refresh-button", "n_clicks")],
        State("user-session", "data"),
    )
    def manage_admin_reports(_, user_session):
        try:
            users_report_data = fetch_users_report(user_session=user_session)
            predictions_report_data = fetch_predictions_reports(
                user_session=user_session
            )
            credits_report_data = fetch_credits_report(user_session=user_session)
            return (
                users_report(users_report_data),
                predictions_report(predictions_report_data),
                credits_report(credits_report_data),
            )
        except Exception as e:
            return (
                error_message("Error fetching users report: " + str(e)),
                error_message("Error fetching predictions report: " + str(e)),
                error_message("Error fetching credits report: " + str(e)),
            )

    @_app.callback(
        [
            Output("deposit-amount", "value"),
            Output("transaction-history-table", "children"),
            Output("current-balance-billing", "children"),
        ],
        [
            Input("deposit-button", "n_clicks"),
        ],
        [
            State("user-session", "data"),
            State("deposit-amount", "value"),
        ],
    )
    def manage_deposit(deposit_clicks, user_session, _deposit_amount):
        if deposit_clicks > 0 and _deposit_amount and _deposit_amount > 0:
            transaction_info = deposit_amount(
                _deposit_amount, user_session=user_session
            )

            if transaction_info:
                balance = fetch_user_balance(user_session=user_session)
                transactions = fetch_transaction_history(user_session=user_session)
                return (
                    "",
                    transaction_history_table(transactions),
                    user_balance(balance),
                )

        raise PreventUpdate

    @_app.callback(
        Output("url", "href"),  # Target the Location component's href
        Input("login-button", "n_clicks"),
        [State("email-input", "value"), State("password-input", "value")],
        prevent_initial_call=True,
    )
    def handle_login(n_clicks, email, password):
        if authenticate_user(email, password):
            return "/dashboard"  # Redirect to dashboard
        return "/login-error"  # Redirect to error page

    # @_app.callback(
    #     [
    #         Output("model-dropdown", "options"),
    #         Output("model-dropdown", "value"),
    #     ],
    #     Input("model-dropdown", "options"),
    #     State("user-session", "data"),
    # )
    # def manage_models(_, user_session):
    #     models = fetch_models(user_session)
    #     dropdown_options = [
    #         {"label": model["name"], "value": model["name"]} for model in models
    #     ]
    #     return dropdown_options, dropdown_options[0]["value"]
    # @_app.callback(
    #     [
    #         Output("model-dropdown", "options"),
    #         Output("model-dropdown", "value"),
    #     ],
    #     Input("model-dropdown", "options"),
    #     State("user-session", "data"),
    # )
    # def manage_models(_, user_session):
    #     try:
    #         models = fetch_models(user_session)
    #         dropdown_options = [
    #             {"label": model["name"], "value": model["name"]} for model in models
    #         ]

    #         # Add defensive check to avoid IndexError
    #         if dropdown_options:
    #             default_value = dropdown_options[0]["value"]
    #         else:
    #             # Provide a fallback option when no models are available
    #             dropdown_options = [{"label": "No models available", "value": ""}]
    #             default_value = ""

    #         return dropdown_options, default_value
    #     except Exception as e:
    #         # Log the error for debugging
    #         print(f"Error in manage_models callback: {str(e)}")
    #         # Return a fallback option
    #         fallback_options = [{"label": "Error loading models", "value": ""}]
    #         return fallback_options, ""
    @_app.callback(
        [Output("model-dropdown", "options"), Output("model-dropdown", "value")],
        [Input("url", "pathname")],  # Trigger on page load
        [State("user-session", "data")],
    )
    def load_models(_, user_session):
        try:
            if not user_session:
                return [{"label": "Login required", "value": ""}], ""

            models = fetch_models(user_session)

            if not models:
                return [{"label": "No models available", "value": ""}], ""

            options = [
                {"label": f"{m['name']} ({m['cost']} credits)", "value": m["name"]}
                for m in models
            ]

            return options, models[0]["name"]

        except Exception as e:
            print(f"Model loading error: {str(e)}")
            return [{"label": "Error loading models", "value": ""}], ""

    @_app.callback(
        [
            Output("prediction-history-table", "children"),
            Output("current-balance-predictions", "children"),
        ],
        [
            Input("predict-button", "n_clicks"),
            Input("upload-data", "contents"),
        ],
        [
            State("user-session", "data"),
            State("model-dropdown", "value"),
        ],
    )
    def manage_predictions(n_clicks, contents, user_session, selected_model):
        if n_clicks > 0 and user_session:
            json = parse_contents(contents)

            send_prediction_request(selected_model, json, user_session)
            predictions = fetch_prediction_history(user_session=user_session)
            balance = fetch_user_balance(user_session=user_session)
            return prediction_history_table(predictions), user_balance(balance)

        raise PreventUpdate

    @_app.callback(
        Output("estimated-cost", "children"),
        [
            Input("model-dropdown", "value"),
            Input("upload-data", "contents"),
        ],
        [State("user-session", "data")],
    )
    def update_estimated_cost(selected_model, contents, user_session):
        global_models = fetch_models(user_session=user_session)
        if selected_model and contents and global_models:
            num_pairs = len(parse_contents(contents))
            total_cost = 0

            for model in global_models:
                if model["name"] == selected_model:
                    total_cost = model["cost"] * max(num_pairs, 1)
                    break
            return estimated_cost(total_cost)
        return estimated_cost(None)

    # Add to the register_callbacks function
    # @_app.callback(
    #     Output("user-session", "data"),
    #     Input({"type": "nav-button", "index": "sign-out"}, "n_clicks"),
    #     prevent_initial_call=True,
    # )
    # def sign_out_callback(_):
    #     return {}  # Clear session

    # @_app.callback(
    #     [
    #         Output("user-session", "data"),  # Clear the session
    #         Output("url", "pathname"),  # Redirect to sign-in
    #     ],
    #     [
    #         Input({"type": "nav-button", "index": "sign-out"}, "n_clicks"),
    #     ],
    #     [
    #         State("user-session", "data"),
    #     ],
    #     prevent_initial_call=True,
    # )
    # def sign_out_callback(sign_out_clicks, user_session):
    #     if sign_out_clicks > 0:
    #         # Clear the user session
    #         cleared_session = {
    #             "is_authenticated": False,
    #             "access_token": None,
    #             "is_superuser": False,
    #         }
    #         # Redirect to sign-in page
    #         return cleared_session, "/sign-in"
    #     raise PreventUpdate


# import base64
# import io
# import json
# from datetime import datetime
# from json import JSONDecodeError, loads

# import pandas as pd
# from dash import ALL, Input, Output, State, callback_context, dcc
# from dash.exceptions import PreventUpdate

# from frontend.data.local_data import authentificated_session
# from frontend.data.remote_data import (
#     authenticate_user,
#     deposit_amount,
#     fetch_credits_report,
#     fetch_models,
#     fetch_prediction_history,
#     fetch_predictions_reports,
#     fetch_transaction_history,
#     fetch_user_balance,
#     fetch_users_report,
#     register_user,
#     send_prediction_request,
# )
# from frontend.layouts.admin_layout import (
#     admin_layout,
#     credits_report,
#     predictions_report,
#     users_report,
# )
# from frontend.layouts.billing_layout import billing_layout, transaction_history_table
# from frontend.layouts.prediction_layout import (
#     estimated_cost,
#     prediction_history_table,
#     prediction_layout,
# )
# from frontend.layouts.sign_in_layout import sign_in_layout
# from frontend.layouts.sign_up_layout import sign_up_layout
# from frontend.ui_kit.components.error_message import error_message
# from frontend.ui_kit.components.navigation import navigation_bar
# from frontend.ui_kit.components.user_balance import user_balance

# sign_page_last_click_timestamp = datetime.now()  # to prevent changing page on update


# def parse_contents(contents):
#     content_type, content_string = contents[0].split(",")
#     decoded = base64.b64decode(content_string)
#     df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
#     json_list = loads(df.to_json(orient="records"))
#     return json_list


# def register_callbacks(_app):
#     @_app.callback(
#         Output("user-session", "data"),
#         [
#             Input("sign-in-session-update", "data"),
#             Input("sign-up-session-update", "data"),
#         ],
#         State("user-session", "data"),
#     )
#     def manage_session(sign_in_data, sign_up_data, current_session):
#         ctx = callback_context

#         if not ctx.triggered:
#             return current_session
#         trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

#         if trigger_id == "sign-in-session-update" and sign_in_data:
#             return sign_in_data
#         elif trigger_id == "sign-up-session-update" and sign_up_data:
#             return sign_up_data

#         return current_session

#     @_app.callback(
#         Output("url", "pathname"),
#         [
#             Input({"type": "nav-button", "index": ALL}, "n_clicks_timestamp"),
#             Input("user-session", "data"),
#         ],
#         State("url", "pathname"),
#         prevent_initial_call=True,
#     )
#     def manage_navigation(n_clicks_timestamp, user_session, pathname):
#         global sign_page_last_click_timestamp
#         ctx = callback_context

#         if (
#             user_session
#             and user_session.get("is_authenticated", False)
#             and pathname in ["/sign-in", "/sign-up"]
#         ):
#             return "/prediction"
#         else:
#             if not ctx.triggered:
#                 raise PreventUpdate

#             button_id = ctx.triggered[0]["prop_id"].split(".")[0]

#             if not button_id:
#                 raise PreventUpdate

#             try:
#                 button_index = json.loads(button_id.replace("'", '"'))["index"]
#             except JSONDecodeError:
#                 raise PreventUpdate

#             click_timestamp = max(n_clicks_timestamp) if n_clicks_timestamp else None

#             if (
#                 click_timestamp
#                 and (datetime.now() - sign_page_last_click_timestamp).total_seconds()
#                 > 1
#             ):
#                 sign_page_last_click_timestamp = datetime.now()
#                 if button_index == "sign-up":
#                     return "/sign-up"
#                 elif button_index == "sign-in":
#                     return "/sign-in"
#             else:
#                 raise PreventUpdate

#     @_app.callback(
#         Output("page-content", "children"),
#         [Input("url", "pathname")],
#         [State("user-session", "data")],
#     )
#     def manage_page_content(pathname, user_session):
#         if user_session and user_session.get("is_authenticated"):
#             if pathname == "/prediction":
#                 return prediction_layout(user_session)
#             elif pathname == "/billing":
#                 return billing_layout(user_session)
#             elif pathname == "/admin":
#                 if user_session.get("is_superuser"):
#                     return admin_layout()
#                 else:
#                     return "403 Access Denied"
#             else:
#                 return "404 Page Not Found"
#         else:
#             if pathname == "/sign-in":
#                 return sign_in_layout()
#             elif pathname == "/sign-up":
#                 return sign_up_layout()
#             else:
#                 return dcc.Location(id="url", href="/sign-in", refresh=True)

#     @_app.callback(Output("nav-bar", "children"), [Input("user-session", "data")])
#     def manage_navigation_bar(user_session):
#         if user_session and user_session.get("is_authenticated"):
#             return navigation_bar(user_session)
#         return ""

#     @_app.callback(
#         [
#             Output("sign-in-session-update", "data"),
#             Output("sign-in-status", "children"),
#         ],
#         [
#             Input({"type": "auth-button", "action": "sign-in"}, "n_clicks"),
#         ],
#         [
#             State("user-session", "data"),
#             State("sign-in-email", "value"),
#             State("sign-in-password", "value"),
#         ],
#         prevent_initial_call=True,
#     )
#     def sign_in_callback(sign_in_clicks, _, sign_in_email, sign_in_password):
#         if sign_in_clicks > 0:
#             user_data, error = authenticate_user(sign_in_email, sign_in_password)
#             if user_data:
#                 new_user_session = authentificated_session(user_data)
#                 return new_user_session, "Sign in successful"
#             return None, error_message(error if error else "Invalid credentials")
#         raise PreventUpdate

#     @_app.callback(
#         [
#             Output("sign-up-session-update", "data"),
#             Output("sign-up-status", "children"),
#         ],
#         [
#             Input({"type": "auth-button", "action": "sign-up"}, "n_clicks"),
#         ],
#         [
#             State("user-session", "data"),
#             State("sign-up-email", "value"),
#             State("sign-up-password", "value"),
#             State("sign-up-name", "value"),
#         ],
#         prevent_initial_call=True,
#     )
#     def sign_up_callback(
#         sign_up_clicks, _, sign_up_email, sign_up_password, sign_up_name
#     ):
#         if sign_up_clicks > 0:
#             user_data, error = register_user(
#                 sign_up_email, sign_up_password, sign_up_name
#             )
#             if user_data:
#                 new_user_session = authentificated_session(user_data)
#                 return new_user_session, "Registration successful"

#             return {}, error_message(error if error else "Registration failed")

#         raise PreventUpdate

#     @_app.callback(
#         [
#             Output("users-report-div", "children"),
#             Output("predictions-report-div", "children"),
#             Output("credits-report-div", "children"),
#         ],
#         [Input("refresh-button", "n_clicks")],
#         State("user-session", "data"),
#     )
#     def manage_admin_reports(_, user_session):
#         try:
#             users_report_data = fetch_users_report(user_session=user_session)
#             predictions_report_data = fetch_predictions_reports(
#                 user_session=user_session
#             )
#             credits_report_data = fetch_credits_report(user_session=user_session)
#             return (
#                 users_report(users_report_data),
#                 predictions_report(predictions_report_data),
#                 credits_report(credits_report_data),
#             )
#         except Exception as e:
#             return (
#                 error_message("Error fetching users report: " + str(e)),
#                 error_message("Error fetching predictions report: " + str(e)),
#                 error_message("Error fetching credits report: " + str(e)),
#             )

#     @_app.callback(
#         [
#             Output("deposit-amount", "value"),
#             Output("transaction-history-table", "children"),
#             Output("current-balance-billing", "children"),
#         ],
#         [
#             Input("deposit-button", "n_clicks"),
#         ],
#         [
#             State("user-session", "data"),
#             State("deposit-amount", "value"),
#         ],
#     )
#     def manage_deposit(deposit_clicks, user_session, _deposit_amount):
#         if deposit_clicks > 0 and _deposit_amount and _deposit_amount > 0:
#             transaction_info = deposit_amount(
#                 _deposit_amount, user_session=user_session
#             )

#             if transaction_info:
#                 balance = fetch_user_balance(user_session=user_session)
#                 transactions = fetch_transaction_history(user_session=user_session)
#                 return (
#                     "",
#                     transaction_history_table(transactions),
#                     user_balance(balance),
#                 )

#         raise PreventUpdate

#     @_app.callback(
#         [
#             Output("model-dropdown", "options"),
#             Output("model-dropdown", "value"),
#         ],
#         Input("model-dropdown", "options"),
#         State("user-session", "data"),
#     )
#     def manage_models(_, user_session):
#         models = fetch_models(user_session)
#         dropdown_options = [
#             {"label": model["name"], "value": model["name"]} for model in models
#         ]
#         return dropdown_options, dropdown_options[0]["value"]

#     @_app.callback(
#         [
#             Output("prediction-history-table", "children"),
#             Output("current-balance-predictions", "children"),
#         ],
#         [
#             Input("predict-button", "n_clicks"),
#             Input("upload-data", "contents"),
#         ],
#         [
#             State("user-session", "data"),
#             State("model-dropdown", "value"),
#         ],
#     )
#     def manage_predictions(n_clicks, contents, user_session, selected_model):
#         if n_clicks > 0 and user_session:
#             json = parse_contents(contents)

#             send_prediction_request(selected_model, json, user_session)
#             predictions = fetch_prediction_history(user_session=user_session)
#             balance = fetch_user_balance(user_session=user_session)
#             return prediction_history_table(predictions), user_balance(balance)

#         raise PreventUpdate

#     @_app.callback(
#         Output("estimated-cost", "children"),
#         [
#             Input("model-dropdown", "value"),
#             Input("upload-data", "contents"),
#         ],
#         [State("user-session", "data")],
#     )
#     def update_estimated_cost(selected_model, contents, user_session):
#         global_models = fetch_models(user_session=user_session)
#         if selected_model and contents and global_models:
#             num_pairs = len(parse_contents(contents))
#             total_cost = 0

#             for model in global_models:
#                 if model["name"] == selected_model:
#                     total_cost = model["cost"] * max(num_pairs, 1)
#                     break
#             return estimated_cost(total_cost)
#         return estimated_cost(None)
