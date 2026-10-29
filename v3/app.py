
from flask import Flask, request, render_template_string
from datetime import datetime
from uuid import uuid4

app = Flask(__name__)

payments = []

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Payment System v3</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f2f5f9;
            margin: 40px;
        }
        .container {
            max-width: 700px;
            margin: auto;
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px #cccccc;
        }
        input, select, button {
            width: 100%;
            padding: 10px;
            margin: 8px 0;
            box-sizing: border-box;
        }
        button {
            background: #1769aa;
            color: white;
            border: none;
            cursor: pointer;
            border-radius: 5px;
        }
        button:hover {
            background: #0d4777;
        }
        .message {
            background: #e5f5e9;
            padding: 12px;
            margin: 12px 0;
            border-radius: 5px;
        }
        .receipt {
            border: 2px dashed #1769aa;
            padding: 18px;
            margin-top: 20px;
            background: #f8fbff;
        }
        .payment {
            border-bottom: 1px solid #ddd;
            padding: 10px 0;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>Payment System - v3</h1>
    <p>Enter payment details, validate them, and generate a demo receipt.</p>

    <form method="POST">
        <label>Customer Name</label>
        <input type="text" name="customer"
               value="{{ customer }}" maxlength="100"
               placeholder="Enter customer name">

        <label>Payment Amount (₹)</label>
        <input type="number" name="amount" step="0.01" min="0.01"
               value="{{ amount }}" placeholder="Enter amount">

        <label>Payment Method</label>
        <select name="method">
            <option value="">Select method</option>
            {% for option in methods %}
            <option value="{{ option }}"
                {% if method == option %}selected{% endif %}>
                {{ option }}
            </option>
            {% endfor %}
        </select>

        <button type="submit" name="action" value="enter">
            Enter Payment Details
        </button>

        <button type="submit" name="action" value="validate">
            Validate Payment
        </button>

        <button type="submit" name="action" value="receipt">
            Generate Receipt
        </button>
    </form>

    {% if message %}
    <div class="message">{{ message }}</div>
    {% endif %}

    {% if receipt %}
    <div class="receipt">
        <h2>Payment Receipt</h2>
        <p><strong>Receipt ID:</strong> {{ receipt.receipt_id }}</p>
        <p><strong>Payment ID:</strong> {{ receipt.payment_id }}</p>
        <p><strong>Customer:</strong> {{ receipt.customer }}</p>
        <p><strong>Amount:</strong> ₹{{ "%.2f"|format(receipt.amount) }}</p>
        <p><strong>Method:</strong> {{ receipt.method }}</p>
        <p><strong>Status:</strong> {{ receipt.status }}</p>
        <p><strong>Date and Time:</strong> {{ receipt.timestamp }}</p>
        <p><em>Demo receipt only — no real payment was processed.</em></p>
    </div>
    {% endif %}

    <h2>Payment Records</h2>
    {% for payment in payments %}
    <div class="payment">
        <strong>{{ payment.customer }}</strong><br>
        Payment ID: {{ payment.payment_id }}<br>
        Amount: ₹{{ "%.2f"|format(payment.amount) }}<br>
        Method: {{ payment.method }}<br>
        Status: {{ payment.status }}
    </div>
    {% else %}
    <p>No payment records yet.</p>
    {% endfor %}
</div>
</body>
</html>
"""


def validate_details(customer, amount_text, method):
    if not customer:
        return None, "Please enter the customer name."

    if len(customer) > 100:
        return None, "Customer name must be 100 characters or fewer."

    try:
        amount = float(amount_text)
    except (ValueError, TypeError):
        return None, "Please enter a valid payment amount."

    if amount <= 0:
        return None, "Payment amount must be greater than zero."

    if method not in ["UPI", "Card", "Net Banking", "Cash"]:
        return None, "Please select a valid payment method."

    return {
        "customer": customer,
        "amount": amount,
        "method": method
    }, None


@app.route("/", methods=["GET", "POST"])
def home():
    message = ""
    receipt = None
    customer = ""
    amount = ""
    method = ""

    if request.method == "POST":
        customer = request.form.get("customer", "").strip()
        amount = request.form.get("amount", "").strip()
        method = request.form.get("method", "").strip()
        action = request.form.get("action", "")

        details, error = validate_details(customer, amount, method)

        if action == "enter":
            message = (
                "Payment details entered. Validate them before "
                "generating a receipt."
            )

        elif action == "validate":
            if error:
                message = error
            else:
                payment = {
                    "payment_id": str(uuid4())[:8].upper(),
                    "customer": details["customer"],
                    "amount": details["amount"],
                    "method": details["method"],
                    "status": "Validated",
                    "timestamp": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "receipt_id": None
                }
                payments.append(payment)
                message = (
                    "Payment details validated successfully. "
                    "You can now generate a demo receipt."
                )

        elif action == "receipt":
            if error:
                message = error
            else:
                # Find the most recent validated matching payment.
                matching_payment = next(
                    (
                        p for p in reversed(payments)
                        if p["customer"] == details["customer"]
                        and p["amount"] == details["amount"]
                        and p["method"] == details["method"]
                        and p["status"] == "Validated"
                    ),
                    None
                )

                if matching_payment is None:
                    message = (
                        "No matching validated payment found. "
                        "Please validate the details first."
                    )
                else:
                    if not matching_payment["receipt_id"]:
                        matching_payment["receipt_id"] = (
                            "RCP-" + str(uuid4())[:8].upper()
                        )

                    receipt = {
                        **matching_payment,
                        "status": "Receipt Generated",
                        "timestamp": datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    }
                    message = "Demo receipt generated successfully."

    return render_template_string(
        HTML,
        message=message,
        receipt=receipt,
        payments=payments,
        customer=customer,
        amount=amount,
        method=method,
        methods=["UPI", "Card", "Net Banking", "Cash"]
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=False)
