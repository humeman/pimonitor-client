
def eq(value, threshold):
    return value == threshold

def geq(value, threshold):
    return value >= threshold

def leq(value, threshold):
    return value <= threshold

def neq(value, threshold):
    return value != threshold

def g(value, threshold):
    return value > threshold

def l(value, threshold):
    return value < threshold

comparisons = {
    "==": eq,
    ">=": geq,
    "<=": leq,
    "!=": neq,
    ">": g,
    "<": l
}