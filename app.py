from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from algorithm import extract_text_from_image, parse_receipt
from PIL import Image, UnidentifiedImageError

app = Flask(__name__)
app.secret_key = "your_secret_key"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.before_request
def make_session_permanent():
    session.permanent = True

def get_session_data():
    parsed_data = session.get("parsed_data", {"items": [], "subtotal": 0, "tax": 0, "tip": 0, "total": 0})
    assignments = session.get("assignments", {})
    return parsed_data, assignments

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        receipt = request.files['receipt']
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], receipt.filename)
        receipt.save(file_path)

        try:
            image = Image.open(file_path)
            extracted_text = extract_text_from_image(file_path)
            session["parsed_data"] = parse_receipt(extracted_text)
            session["assignments"] = {}
        except UnidentifiedImageError:
            flash("Unsupported image format. Please upload a valid receipt image.")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"An error occurred while processing the receipt: {str(e)}")
            return redirect(url_for('index'))

        return redirect(url_for('safety'))

    return render_template("index.html")

@app.route("/safety", methods=["GET", "POST"])
def safety():
    parsed_data, _ = get_session_data()

    if request.method == "POST":
        num_people = int(request.form.get("num_people"))
        session["num_people"] = num_people

        people_names = [request.form.get(f"person_name_{i}") for i in range(num_people)]
        session["people_names"] = people_names

        edited_items = []
        item_names = request.form.getlist("item_name_")
        item_quantities = request.form.getlist("item_quantity_")
        item_prices = request.form.getlist("item_price_")

        for i in range(len(item_names)):
            try:
                item_name = item_names[i]
                item_quantity = int(item_quantities[i])
                item_price = float(item_prices[i])
                edited_items.append({"name": item_name, "quantity": item_quantity, "price": item_price})
            except ValueError:
                flash("Invalid input. Please enter valid numbers for quantity and price.")
                return render_template("safety.html", parsed_data=parsed_data)

        parsed_data["items"] = edited_items
        parsed_data["subtotal"] = float(request.form.get("subtotal"))
        parsed_data["tax"] = float(request.form.get("tax"))
        parsed_data["tip"] = float(request.form.get("tip"))
        parsed_data["total"] = float(request.form.get("total"))

        session["parsed_data"] = parsed_data
        session.modified = True
        return redirect(url_for('assign_items'))

    return render_template("safety.html", parsed_data=parsed_data)

@app.route("/assign_items", methods=["GET", "POST"])
def assign_items():
    parsed_data, assignments = get_session_data()
    num_people = session.get("num_people", 1)
    people_names = session.get("people_names", [])

    if request.method == "POST":
        assignments = {name: {"items": [], "shared": []} for name in people_names}

        for key, values in request.form.lists():
            if key.startswith("item_"):
                item_index = int(key.split("_")[1].replace("[]", ""))
                item_name = parsed_data["items"][item_index]["name"]

                if len(values) > 1:
                    for person in values:
                        assignments[person]["shared"].append(item_name)
                else:
                    assignments[values[0]]["items"].append(item_name)

        session["assignments"] = assignments
        session.modified = True

        return redirect(url_for('results'))

    return render_template("assign_items.html", parsed_data=parsed_data, assignments=assignments, num_people=num_people)

@app.route("/results", methods=["GET", "POST"])
def results():
    parsed_data = session.get("parsed_data", None)
    assignments = session.get("assignments", {})

    if not assignments:
        flash("Error processing data. Please reassign items.")
        return redirect(url_for('assign_items'))

    individual_totals = {}
    grand_total = 0

    for person, data in assignments.items():
        total = sum(
            next((item["price"] for item in parsed_data["items"] if item["name"] == item_name), 0)
            for item_name in data["items"]
        )

        for shared_item in data["shared"]:
            shared_price = next((item["price"] for item in parsed_data["items"] if item["name"] == shared_item), 0)
            total += shared_price / len(assignments)

        subtotal = parsed_data["subtotal"]
        tax_share = (total / subtotal) * parsed_data["tax"] if subtotal > 0 else 0
        tip_share = (total / subtotal) * parsed_data["tip"] if subtotal > 0 else 0

        individual_totals[person] = {
            "items": data["items"],
            "shared": data["shared"],
            "total": round(total + tax_share + tip_share, 2),
            "tax_share": round(tax_share, 2),
            "tip_share": round(tip_share, 2),
        }
        grand_total += individual_totals[person]["total"]

    session["grand_total"] = grand_total

    if round(grand_total, 2) != round(parsed_data['total'], 2):
        flash("Error: The calculated total does not match the expected total.")
        return redirect(url_for('assign_items'))

    return render_template("results.html", parsed_data=parsed_data, assignments=assignments, individual_totals=individual_totals)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
