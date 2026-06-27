last_signals = {}

def is_new_signal(signal):

    sym = signal["symbol"]
    score = signal["signal_score"]

    if sym in last_signals:
        if abs(last_signals[sym] - score) < 0.01:
            return False

    last_signals[sym] = score
    return True
