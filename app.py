from helpers import black_scholes, get_color
from flask import Flask, request, jsonify, render_template
import plotly.graph_objs as go
import numpy as np

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    current_price = data['price']
    strike_price = data['strike']
    maturity = data['maturity']
    volatility = data['volatility']
    interest = data['interest']

    prices = black_scholes(current_price, strike_price, maturity, volatility, interest)

    return jsonify(prices)

@app.route('/update_heatmaps', methods=['POST'])
def update_heatmaps():
    data = request.get_json()
    strike_price = data['strike']
    maturity = data['maturity']
    interest = data['interest']

    min_spot = data['minSpot']
    max_spot = data['maxSpot']
    min_vol = data['minVol']
    max_vol = data['maxVol']

    x = np.linspace(min_spot, max_spot, 7)  # Underlying price range
    y = np.linspace(min_vol, max_vol, 7)  # Volatility range
    X, Y = np.meshgrid(x, y)
    Call_Z = np.zeros_like(X)
    Put_Z = np.zeros_like(X)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            Call_Z[i, j] = black_scholes(X[i, j], strike_price, maturity, Y[i, j], interest)["call_price"]
            Put_Z[i, j] = black_scholes(X[i, j], strike_price, maturity, Y[i, j], interest)["put_price"]

    threshold_call = np.max(Call_Z) * 0.15 + np.min(Call_Z)
    threshold_put = np.max(Put_Z) * 0.15 + np.min(Put_Z)

    call_annotations = [
        dict(
            x=x[j],
            y=y[i],
            text=f"{Call_Z[i, j]:.2f}",
            showarrow=False,
            font=dict(color=get_color(Call_Z[i, j], threshold_call))
        )
        for i in range(Call_Z.shape[0]) for j in range(Call_Z.shape[1])
    ]

    # Create annotations for put prices
    put_annotations = [
        dict(
            x=x[j],
            y=y[i],
            text=f"{Put_Z[i, j]:.2f}",
            showarrow=False,
            font=dict(color=get_color(Put_Z[i, j], threshold_put))
        )
        for i in range(Put_Z.shape[0]) for j in range(Put_Z.shape[1])
    ]

    call_heatmap = go.Heatmap(z=Call_Z.tolist(), x=x.tolist(), y=y.tolist(), colorscale='viridis')
    put_heatmap = go.Heatmap(z=Put_Z.tolist(), x=x.tolist(), y=y.tolist(), colorscale='viridis')

    call_layout = go.Layout(
        title="Call Price",
        xaxis_title="Spot Price",
        yaxis_title="Volatility",
        xaxis=dict(
            tickvals=x.tolist(),  # Positions for the x-axis ticks
            ticktext=[f"{val:.2f}" for val in x],  # Labels for the x-axis ticks (formatted)
            ticklen=5,
            ticks="outside"
        ),
        yaxis=dict(
            tickvals=y.tolist(),  # Positions for the y-axis ticks
            ticktext=[f"{val:.2f}" for val in y],  # Labels for the y-axis ticks (formatted)
            ticklen=5,
            ticks="outside"
        ),
        plot_bgcolor='#121212',  # Set the plot area background color to black
        paper_bgcolor='#121212', # Set the overall background color to black
        font=dict(
            color='#FFFFFF'  # Set the font color (for text, axis labels) to white
        ),
        annotations=call_annotations
    )

    put_layout = go.Layout(
        title="Put Price",
        xaxis_title="Spot Price",
        yaxis_title="Volatility",
        xaxis=dict(
            tickvals=x.tolist(),  # Positions for the x-axis ticks
            ticktext=[f"{val:.2f}" for val in x],  # Labels for the x-axis ticks (formatted)
            ticklen=5,
            ticks="outside"
        ),
        yaxis=dict(
            tickvals=y.tolist(),  # Positions for the y-axis ticks
            ticktext=[f"{val:.2f}" for val in y],  # Labels for the y-axis ticks (formatted)
            ticklen=5,
            ticks="outside"
        ),
        plot_bgcolor='#121212',  # Set the plot area background color to black
        paper_bgcolor='#121212', # Set the overall background color to black
        font=dict(
            color='#FFFFFF'  # Set the font color (for text, axis labels) to white
        ),
        annotations=put_annotations
    )

    call_fig = go.Figure(data=[call_heatmap], layout=call_layout)
    put_fig = go.Figure(data=[put_heatmap], layout=put_layout)

    # Convert the figure to a dictionary that is JSON serializable
    call_fig_dict = call_fig.to_dict()
    put_fig_dict = put_fig.to_dict()

    heatmaps = [call_fig_dict, put_fig_dict]

    # Return the dictionary as a JSON response
    return jsonify(heatmaps)


