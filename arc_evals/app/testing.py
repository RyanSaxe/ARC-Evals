import dash
import dash_bootstrap_components as dbc
from dash import html


def gradient_button(value):
    # Define the start and end colors
    start_color = "red"
    end_color = "green"

    # Calculate the percentage based on the value
    percentage = value * 100

    # Create the CSS gradient style with multiple color stops
    gradient_style = {
        "background": f"linear-gradient(90deg, {start_color} 0%, {start_color} {percentage}%, {end_color} {percentage}%, {end_color} 100%)"
    }

    # Create the button with the gradient style
    button = dbc.Button("Gradient Button", style=gradient_style)

    return button


# Example usage
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([gradient_button(0), html.Br(), gradient_button(0.5), html.Br(), gradient_button(1)])

if __name__ == "__main__":
    app.run_server(debug=True)
