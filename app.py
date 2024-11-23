from flask import Flask, render_template, request

app = Flask(__name__)


def british_tax_rate(gross_salary):
    """
    Calculate take-home pay in the UK for the 2023/2024 tax year.

    Args:
        gross_salary (float): Annual gross salary in GBP.

    Returns:
        dict: A dictionary with a breakdown of tax, NIC, and take-home pay.
    """
    # Define tax brackets and rates
    tax_brackets = [
        (0, 12570, 0.0),  # Personal Allowance
        (12571, 50270, 0.20),  # Basic rate
        (50271, 125140, 0.40),  # Higher rate
        (125141, float('inf'), 0.45),  # Additional rate
    ]

    # Define National Insurance thresholds and rates
    ni_brackets = [
        (0, 12569, 0.0),  # Below the Lower Earnings Limit
        (12570, 50270, 0.08),  # Primary threshold
        (50271, float('inf'), 0.02),  # Upper earnings limit
    ]

    # Adjust personal allowance for incomes over £100,000
    personal_allowance = 12570
    if gross_salary > 100000:
        reduction = (gross_salary - 100000) / 2
        personal_allowance = max(0, 12570 - reduction)
        # Update tax brackets accordingly
        tax_brackets[0] = (0, personal_allowance, 0.0)
        tax_brackets[1] = (personal_allowance + 1, 50270, 0.20)

    # Calculate income tax
    tax = 0.0
    for lower, upper, rate in tax_brackets:
        if gross_salary > lower:
            taxable_income = min(gross_salary, upper) - lower
            tax += taxable_income * rate

    # Calculate National Insurance
    ni = 0.0
    for lower, upper, rate in ni_brackets:
        if gross_salary > lower:
            ni_income = min(gross_salary, upper) - lower
            ni += ni_income * rate

    # Calculate take-home pay
    take_home = gross_salary - tax - ni

    return {
        "Gross Salary": gross_salary,
        "Income Tax": round(tax, 2),
        "National Insurance": round(ni, 2),
        "Take-Home Pay": round(take_home, 2),
    }


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get gross salary from the form
        gross_salary = float(request.form.get('gross_salary', 0))
        # Calculate the tax breakdown
        result = british_tax_rate(gross_salary)
        return render_template('result.html', result=result)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
