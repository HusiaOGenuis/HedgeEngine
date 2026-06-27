def smooth_risk(signal, drawdown):

    if drawdown < -0.10:
        signal["recommended_risk"] *= 0.5
    elif drawdown < -0.20:
        signal["recommended_risk"] *= 0.25

    return signal