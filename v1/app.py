
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
    <title>Payment System - v1</title>
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
        h1 { color: #1d4ed8; margin-bottom: 5px; }
        .subtitle { color: #64748b; margin-bottom: 25px; }
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
            margin-top: 22px;
            padding: 12px;
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover { background: #1d4ed8; }
        .message {
            margin-top: 20px;
            padding: 15px;
            background: #dcfce7;
            border-radius: 6px;
        }
        .payment {
            margin-top: 12px;
            padding: 14px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
        }
        .amount { color: #15803d; font-weight: bold; }
        .note { color: #64748b; font-size: 13px; }
    </style>
</head>
<body>
<div class="container">
    <h1>Payment System</h1>
    <p class="subtitle">Version 1 — Enter Payment Details</p>

    <form method="POST" action="/enter">
        <label for="customer">Customer Name</label>
        <input id="customer" name="customer" required
               maxlength="100" placeholder="Enter customer name">

        <label for="amount">Payment Amount (₹)</label>
        <input id="amount" name="amount" type="number"
               min="0.01" step="0.01" required placeholder="Enter amount">

        <label for="method">Payment Method</label>
        <select id="method" name="method" required>
            <option value="">Select payment method</option>
            <option value="UPI">UPI</option>
            <option value="Card">Debit/Credit Card</option>
            <option value="Net Banking">Net Banking</option>
            <option value="Cash">Cash</option>
        </select>

        <button type="submit">Enter Payment</button>
    </form>

    {% if message %}
    <div class="message">
        <strong>{{ message }}</strong><br>
        Payment ID: {{ payment_id }}<br>
        Customer: {{ customer }}<br>
        Amount: ₹{{ amount }}<br>
        Method: {{ method }}<br>
        Time: {{ time }}
    </div>
    {% endif %}

    <h2>Entered Payments</h2>
    {% for p in payments %}
    <div class="payment">
        <strong>{{ p.customer }}</strong><br>
        <span class="amount">₹{{ p.amount }}</span><br>
        Method: {{ p.method }}<br>
        Payment ID: {{ p.id }}
    </div>
    {% else %}
    <p>No payments entered yet.</p>
    {% endfor %}

    <p class="note">
        Demonstration only. No real money is transferred.
        Payments are stored in memory and reset when the app restarts.
    </p>
</div>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML, payments=payments)


@app.route("/enter", methods=["POST"])
def enter_payment():
    customer = request.form.get("customer", "").strip()
    method = request.form.get("method", "").strip()

    try:
        amount = float(request.form.get("amount", ""))
    except (ValueError, TypeError):
        return "Please enter a valid amount.", 400

    if not customer or len(customer) > 100 or method not in {
        "UPI", "Card", "Net Banking", "Cash"
    } or amount <= 0:
        return "Invalid payment details. Please go back and try again.", 400

    payment = {
        "id": str(uuid.uuid4())[:8].upper(),
        "customer": customer,
        "amount": f"{amount:.2f}",
        "method": method,
        "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }

    payments.insert(0, payment)

    return render_template_string(
        HTML,
        payments=payments,
        message="Payment details entered successfully!",
        payment_id=payment["id"],
        customer=payment["customer"],
        amount=payment["amount"],
        method=payment["method"],
        time=payment["time"]
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
