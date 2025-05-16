from dash import html

from frontend.ui_kit.styles import secondary_button_style


def navigation_bar(user_session):
    """
    Creates a navigation bar with appropriate buttons based on user role
    """
    nav_items = [
        html.Button(
            "Predictions",
            id={"type": "nav-button", "index": "prediction"},
            n_clicks_timestamp=0,
            style=secondary_button_style,
        ),
        html.Button(
            "Billing",
            id={"type": "nav-button", "index": "billing"},
            n_clicks_timestamp=0,
            style=secondary_button_style,
        ),
    ]

    # Add admin button if user is a superuser
    if user_session.get("is_superuser"):
        nav_items.append(
            html.Button(
                "Admin",
                id={"type": "nav-button", "index": "admin"},
                n_clicks_timestamp=0,
                style=secondary_button_style,
            )
        )

    # Add sign out button
    nav_items.append(
        html.Button(
            "Sign Out",
            id={"type": "nav-button", "index": "sign-out"},
            n_clicks_timestamp=0,
            style={
                **secondary_button_style,
                "backgroundColor": "#f44336",
                "float": "right",
            },
        )
    )

    return html.Div(
        nav_items,
        style={
            "padding": "10px",
            "backgroundColor": "#f8f9fa",
            "marginBottom": "20px",
            "borderBottom": "1px solid #dee2e6",
        },
    )
