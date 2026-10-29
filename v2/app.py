
from flask import Flask, render_template_string, request
from datetime import datetime
import uuid

app = Flask(__name__)

payments = []

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Payment System - v2</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            margin: 0;
            padding: 30px 15px;
            color: #1e293b;
        }
        .container {
            max-width: 650px;
            margin: auto;
            background: white;
            padding: 28px;
            border-radius: 12px;
            box-shadow: 0 4px 18px #00000012;
        }
        h1 { color: #1d4ed8; }
        .subtitle { color: #64748b; }
        label {
            display: block;
            margin-top: 15px;
            margin-bottom: 6px;
            font-weight: bold;
        }
        input, select {
            width: 100%;
            padding: 11px;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            margin-top: 15px;
            padding: 12px;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
        }
        .enter { background: #64748b; }
        .validate { background: #2563eb; }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 6px;
        }
        .success { background: #dcfce7; color: #166534; }
        .error { background: #fee2e2; color: #991b1b; }
        .payment {
            margin-top: 12px;
            padding: 14px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
        }
        .note { color: #64748b; font-size: 13px; }
    </style>
</head>
<body>
<div class="container">
    <h1>Payment System</h1>
    <p class="subtitle">Version 2 — Enter and Validate Payments</p>

    <form method="POST">
        <label for="customer">Customer Name</label>
        <input id="customer" name="customer" maxlength="100"
               value="{{ customer }}" placeholder="Enter customer name"
               required>

        <label for="amount">Payment Amount (₹)</label>
        <input id="amount" name="amount" type="number"
               min="0.01" step="0.01" value="{{ amount }}"
               placeholder="Enter amount" required>

        <label for="method">Payment Method</label>
        <select id="method" name="method" required>
            <option value="">Select payment method</option>
            {% for m in methods %}
            <option value="{{ m }}" {% if method == m %}selected{% endif %}>
                {{ m }}
            </option>
            {% endfor %}
        </select>

        <button class="enter" type="submit" name="action" value="enter">
            Enter Payment Details
        </button>
        <button class="validate" type="submit" name="action" value="validate">
            Validate Payment
        </button>
    </form>

    {% if message %}
    <div class="result {{ result_class }}">
        <strong>{{ message }}</strong>
        {% if payment %}
        <p>Payment ID: {{ payment.id }}</p>
        <p>Customer: {{ payment.customer }}</p>
        <p>Amount: ₹{{ payment.amount }}</p>
        <p>Method: {{ payment.method }}</p>
        <p>Status: {{ payment.status }}</p>
        {% endif %}
    </div>
    {% endif %}

    <h2>Payment Records</h2>
    {% for p in payments %}
    <div class="payment">
        <strong>{{ p.customer }}</strong><br>
        Amount: ₹{{ p.amount }}<br>
        Method: {{ p.method }}<br>
        Status: {{ p.status }}<br>
        Payment ID: {{ p.id }}
    </div>
    {% else %}
    <p>No payment records yet.</p>
    {% endfor %}

    <p class="note">
        Demo only. No real money is transferred. Records are stored in memory
        and reset when the application restarts.
    </p>
</div>
</body>
</html>
"""

METHODS = ["UPI", "Card", "Net Banking", "Cash"]


@app.route("/", methods=["GET", "POST"])
def home():
    message = ""
    result_class = ""
    payment = None
    customer = ""
    amount = ""
    method = ""

    if request.method == "POST":
        action = request.form.get("action", "")
        customer = request.form.get("customer", "").strip()
        amount = request.form.get("amount", "").strip()
        method = request.form.get("method", "").strip()

        if action == "enter":
            message = (
                "Details entered. Click Validate Payment to check them."
            )
            result_class = "success"

        elif action == "validate":
            try:
                numeric_amount = float(amount)
                valid_amount = numeric_amount > 0
            except (ValueError, TypeError):
                numeric_amount = 0
                valid_amount = False

            if (
                not customer
                or len(customer) > 100
                or not valid_amount
                or method not in METHODS
            ):
                message = (
                    "Validation failed. Enter a customer name, "
                    "a positive amount, and a valid payment method."
                )
                result_class = "error"
            else:
                payment = {
                    "id": str(uuid.uuid4())[:8].upper(),
                    "customer": customer,
                    "amount": f"{numeric_amount:.2f}",
                    "method": method,
                    "status": "Validated",
                    "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                }

                payments.insert(0, payment)
                message = "Payment details validated successfully!"
                result_class = "success"

    return render_template_string(
        HTML,
        payments=payments,
        methods=METHODS,
        customer=customer,
        amount=amount,
        method=method,
        message=message,
        result_class=result_class,
        payment=payment
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
