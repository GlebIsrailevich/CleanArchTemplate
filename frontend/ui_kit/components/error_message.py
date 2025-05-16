from dash import html


def error_message(message):
    """
    Displays an error message with appropriate styling
    """
    if not message:
        return None

    return html.Div(
        message,
        style={
            "color": "#f44336",
            "backgroundColor": "#ffebee",
            "padding": "10px",
            "borderRadius": "4px",
            "margin": "10px 0",
            "fontFamily": "Arial, sans-serif",
            "fontSize": "14px",
            "border": "1px solid #f44336",
        },
    )
