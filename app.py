from flask import Flask, render_template, request
from datetime import date

app = Flask(__name__)

PERSONAL_ALLOWANCE = 12570

UK_TAX_BANDS = [
    (0, PERSONAL_ALLOWANCE, 0.0),
    (PERSONAL_ALLOWANCE, 50270, 0.20),
    (50270, 125140, 0.40),
    (125140, float('inf'), 0.45),
]

SCOTLAND_TAX_BANDS = [
    (0, PERSONAL_ALLOWANCE, 0.0),
    (PERSONAL_ALLOWANCE, 15397, 0.19),
    (15397, 27491, 0.20),
    (27491, 43662, 0.21),
    (43662, 75000, 0.42),
    (75000, 125140, 0.45),
    (125140, float('inf'), 0.48),
]

NI_BANDS = [
    (0, PERSONAL_ALLOWANCE, 0.0),
    (PERSONAL_ALLOWANCE, 50270, 0.08),
    (50270, float('inf'), 0.02),
]

STUDENT_LOAN_THRESHOLDS = {
    "Plan 1": (26065, 0.09),
    "Plan 2": (28470, 0.09),
    "Plan 4": (32745, 0.09),
    "Plan 5": (float('inf'), 0.09),
    "PGL": (21000, 0.06),
}


def apply_bands(amount, bands):
    total = 0.0
    for lower, upper, rate in bands:
        if amount > lower:
            taxable = min(amount, upper) - lower
            total += taxable * rate
    return total


def calculate_pay(gross_salary, region='UK', student_plan=None, pension_rate=0.0):
    pension = gross_salary * pension_rate / 100
    taxable_salary = max(0, gross_salary - pension)
    bands = SCOTLAND_TAX_BANDS if region.lower() == 'scotland' else UK_TAX_BANDS
    income_tax = apply_bands(taxable_salary, bands)
    ni = apply_bands(taxable_salary, NI_BANDS)
    sl_repayment = 0.0
    if student_plan in STUDENT_LOAN_THRESHOLDS:
        threshold, rate = STUDENT_LOAN_THRESHOLDS[student_plan]
        if taxable_salary > threshold:
            sl_repayment = (taxable_salary - threshold) * rate
    net_pay = gross_salary - income_tax - ni - sl_repayment - pension
    monthly = net_pay / 12
    weekly = net_pay / 52
    eff_tax_rate = income_tax / gross_salary if gross_salary else 0
    eff_ni_rate = ni / gross_salary if gross_salary else 0
    return {
        'gross': round(gross_salary, 2),
        'pension_contrib': round(pension, 2),
        'income_tax': round(income_tax, 2),
        'national_insurance': round(ni, 2),
        'student_loan': round(sl_repayment, 2),
        'net_annual': round(net_pay, 2),
        'net_monthly': round(monthly, 2),
        'net_weekly': round(weekly, 2),
        'eff_tax_rate': round(eff_tax_rate * 100, 2),
        'eff_ni_rate': round(eff_ni_rate * 100, 2),
        'region': region,
        'student_plan': student_plan,
        'pension_rate': pension_rate,
    }


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        gross = float(request.form.get('gross_salary', 0))
        region = request.form.get('region', 'UK')
        student_plan = request.form.get('student_loan_plan')
        pension_rate = float(request.form.get('pension_rate', 0))
        result = calculate_pay(gross, region, student_plan, pension_rate)
        return render_template('result.html', result=result)
    return render_template('index.html')


from flask import jsonify


@app.route('/calculate-tax')
def calculate_tax_api():
    gross = float(request.args.get('gross_salary', 0))
    region = request.args.get('region', 'UK')
    student_plan = request.args.get('student_loan_plan')
    pension_rate = float(request.args.get('pension_rate', 0))
    result = calculate_pay(gross, region, student_plan, pension_rate)
    return jsonify(result)



if __name__ == '__main__':
    app.run(debug=True)
