def calculate_emi(principal, annual_interest_rate, tenure_years):
    monthly_interest_rate = annual_interest_rate / (12 * 100)
    number_of_payments = tenure_years * 12
    if monthly_interest_rate == 0:
        return round(principal / number_of_payments, 2)
    emi = principal * monthly_interest_rate * ((1 + monthly_interest_rate) ** number_of_payments) / (((1 + monthly_interest_rate) ** number_of_payments) - 1)
    return round(emi, 2)
