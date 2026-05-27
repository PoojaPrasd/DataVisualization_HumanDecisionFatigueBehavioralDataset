from dash import Dash
import dash_bootstrap_components as dbc
try:
    from .data_loader import df
    from .layout import create_layout
except ImportError:
    from data_loader import df
    from layout import create_layout

# Initialize the Dash app with a Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Neuropulse Dashboard"

# Set the layout (Static injection, no callbacks required as global filters were removed)
app.layout = create_layout(df)

# We provide a main execution block to allow running the app directly
if __name__ == '__main__':
    # Run the server on localhost port 8050
    app.run(debug=True, port=8050)
