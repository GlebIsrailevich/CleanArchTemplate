from dash import dcc, html

from frontend.ui_kit.styles import (
    heading2_style,
    input_style,
    primary_button_style,
    secondary_button_style,
    text_style,
)

# Updated Input Style for Consistency
updated_input_style = {**input_style, "marginBottom": "15px", "width": "100%"}


# Components
def sign_up_form():
    return html.Div(
        [
            dcc.Input(
                id="sign-up-email",
                type="email",
                placeholder="Email",
                autoFocus=True,
                style=updated_input_style,
            ),
            dcc.Input(
                id="sign-up-password",
                type="password",
                placeholder="Password",
                style=updated_input_style,
            ),
            dcc.Input(
                id="sign-up-name",
                type="text",
                placeholder="Name",
                style=updated_input_style,
            ),
            html.Div(
                [
                    html.Button(
                        "Sign Up",
                        id={"type": "auth-button", "action": "sign-up"},
                        n_clicks=0,
                        style=primary_button_style,
                    ),
                    html.Button(
                        "Sign In Page",
                        id={"type": "nav-button", "index": "sign-in"},
                        n_clicks=0,
                        style=secondary_button_style,
                    ),
                ],
                style={"display": "flex", "justifyContent": "space-between"},
            ),
        ],
        style={
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center",
            "justifyContent": "center",
        },
    )


# Layout
def sign_up_layout():
    return html.Div(
        [
            html.H2("Sign Up", style=heading2_style),
            sign_up_form(),
            html.Div(id="sign-up-status", style=text_style),
        ],
        style={"maxWidth": "500px", "margin": "0 auto", "padding": "20px"},
    )


# from frontend.callbacks.callbacks import register_user
# def handle_sign_up(n_clicks, email, password, name):
#     try:
#         response, error = register_user(email, password, name)
#         if error:
#             return error_message(error), ""

#         if "error" in response:
#             return error_message(response["detail"]), ""

#         return redirect('/'), None

#     except Exception as e:
#         return error_message(str(e)), ""
