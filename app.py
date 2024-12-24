from flask import Flask, render_template, request

app = Flask(__name__)


def british_tax_rate(gross_salary, student_loan_plan=None):
    """
    Calculate take-home pay in the UK for the 2023/2024 tax year, with optional student loan repayment.

    Args:
        gross_salary (float): Annual gross salary in GBP.
        student_loan_plan (str): Optional; Student loan repayment plan ('Plan 1', 'Plan 2', 'Plan 4', 'PGL').

    Returns:
        dict: A dictionary with a breakdown of tax, NIC, student loan, and take-home pay.
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

    # Student loan repayment thresholds and rates
    student_loan_thresholds = {
        "Plan 1": (22015, 0.09),
        "Plan 2": (27295, 0.09),
        "Plan 4": (27660, 0.09),
        "PGL": (21000, 0.06),
    }

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

    # Calculate student loan repayment
    student_loan_repayment = 0.0
    if student_loan_plan in student_loan_thresholds:
        threshold, rate = student_loan_thresholds[student_loan_plan]
        if gross_salary > threshold:
            student_loan_repayment = (gross_salary - threshold) * rate

    # Calculate take-home pay
    take_home = gross_salary - tax - ni - student_loan_repayment

    return {
        "Gross Salary": gross_salary,
        "Income Tax": round(tax, 2),
        "National Insurance": round(ni, 2),
        "Student Loan Repayment": round(student_loan_repayment, 2),
        "Take-Home Pay": round(take_home, 2),
    }


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check which form was submitted
        if 'gross_salary_1' in request.form and 'gross_salary_2' in request.form:
            # Comparison form
            salary1 = float(request.form.get('gross_salary_1', 0))
            salary2 = float(request.form.get('gross_salary_2', 0))
            result1 = british_tax_rate(salary1)
            result2 = british_tax_rate(salary2)
            return render_template('result.html', result1=result1, result2=result2, comparison=True)
        elif 'gross_salary' in request.form:
            salary = float(request.form.get('gross_salary', 0))
            student_loan_plan = request.form.get('student_loan_plan', None)
            result = british_tax_rate(salary, student_loan_plan)
            return render_template('result.html', result=result, comparison=False)

    return render_template('index.html')


@app.route('/calculate-tax')
def calculate_tax():
    gross_salary = float(request.args.get('gross_salary', 0))
    result = british_tax_rate(gross_salary)
    return result


if __name__ == '__main__':
    app.run(debug=True)
