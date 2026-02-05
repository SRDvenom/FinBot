import re

def calculate_emi(principal, rate, years):
    r = rate / (12 * 100)
    n = years * 12
    emi = (principal * r * (1 + r)**n) / ((1 + r)**n - 1)
    return round(emi, 2)

def calculate_sip(investment, rate, years):
    months = years * 12
    monthly_rate = rate / (12 * 100)
    value = investment * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
    return round(value, 2)

def handle_financial_calculations(message):
    msg = message.lower()

    # EMI pattern
    if "emi" in msg:
        match = re.search(r'(\d+)\D+(\d+)\D+(\d+)', msg)
        if match:
            principal, rate, years = map(float, match.groups())
            emi = calculate_emi(principal, rate, years)
            return f"Approximate EMI for ₹{int(principal)} at {rate}% for {int(years)} years is ₹{emi}/month."

    # SIP pattern
    if "sip" in msg:
        match = re.search(r'(\d+)\D+(\d+)\D+(\d+)', msg)
        if match:
            investment, rate, years = map(float, match.groups())
            value = calculate_sip(investment, rate, years)
            return f"Your SIP of ₹{int(investment)} at {rate}% for {int(years)} years will grow to around ₹{value}."

    return None  # not a calculation query
