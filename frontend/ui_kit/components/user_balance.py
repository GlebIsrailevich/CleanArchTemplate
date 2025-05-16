from dash import html

from frontend.ui_kit.styles import text_style


def user_balance(balance):
    """
    Displays the user's current balance
    """
    if not balance:
        return html.Div("No balance information available", style=text_style)

    return html.Div(
        [
            html.H3("Current Balance", style=text_style),
            html.Div(
                f"${balance.get('balance', 0):,.2f}",
                style={
                    **text_style,
                    "fontSize": "24px",
                    "fontWeight": "bold",
                    "color": "#4CAF50",
                    "marginBottom": "20px",
                },
            ),
        ]
    )
