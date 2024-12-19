from numpy import exp, sqrt, log
from scipy.stats import norm

def black_scholes(current_price, strike_price, time_to_maturity, volatility, interest_rate):
    d1 = (
        log(current_price / strike_price) +
        (interest_rate + (volatility**2 / 2)) * time_to_maturity
        ) / (
        volatility * sqrt(time_to_maturity)
        )

    d2 = d1 - (volatility * sqrt(time_to_maturity))

    call_price = (
        current_price * norm.cdf(d1)
        ) - (
        strike_price * exp(-(interest_rate * time_to_maturity)) * norm.cdf(d2)
        )

    put_price = (
            strike_price * exp(-(interest_rate * time_to_maturity)) * norm.cdf(-(d2))
        ) - (
            current_price * norm.cdf(-(d1))
        )

    return {"call_price": call_price, "put_price": put_price}

def get_color(z_value, threshold):
    if z_value < threshold:
        return "white"
    else:
        return "black"


