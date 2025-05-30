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


def authentificated_session(user_data):
    """
    Creates a session object from user data returned by the API
    """
    return {
        "id": user_data.get("id"),
        "email": user_data.get("email"),
        "name": user_data.get("name"),
        "is_superuser": user_data.get("is_superuser", False),
        "is_authenticated": True,
        "access_token": user_data.get("access_token"),
    }
