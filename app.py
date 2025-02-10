from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from algorithm import extract_text_from_image, parse_receipt
from PIL import Image, UnidentifiedImageError
import pytesseract
import math


# Manually set Tesseract path on Render
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


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

        print(f"Uploaded file saved to: {file_path}")  # Debugging log

        try:
            image = Image.open(file_path)
            extracted_text = extract_text_from_image(file_path)

            print(f"Extracted Text: {extracted_text}")  # Debugging log

            session["parsed_data"] = parse_receipt(extracted_text)
            session["assignments"] = {}

            print("Parsed Data in Session (Index):", session.get("parsed_data"))

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

    # Debugging: Print the parsed data when reaching the safety page
    print("Parsed Data in Safety Screen:", parsed_data)

    if request.method == "POST":
        num_people = int(request.form.get("num_people"))
        session["num_people"] = num_people

        people_names = [request.form.get(f"person_name_{i}") for i in range(num_people)]
        session["people_names"] = people_names

        edited_items = session.get("parsed_data", {}).get("items", [])  # Ensure existing items are carried forward
        item_names = request.form.getlist("item_name_")
        item_quantities = request.form.getlist("item_quantity_")
        item_prices = request.form.getlist("item_price_")

        new_items = []  # Store newly entered items
        for i in range(len(item_names)):
            try:
                item_name = item_names[i].strip()
                item_quantity = int(item_quantities[i])
                item_price = float(item_prices[i]) / item_quantity  # Split price evenly per unit
                
                # Instead of storing one entry with quantity > 1, store multiple entries
                for _ in range(item_quantity):
                    new_items.append({"name": item_name, "price": item_price})  # Quantity is implied
                
            except ValueError:
                flash("Invalid input. Please enter valid numbers for quantity and price.")
                return render_template("safety.html", parsed_data=parsed_data)

        # Append new items instead of overwriting
        parsed_data["items"] = edited_items + new_items  
  

        session["parsed_data"] = parsed_data  # Explicitly update session
        session.modified = True

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

    # Debugging: Print session data to check its state
    print("Parsed Data in Session (Assign Items):", parsed_data)
    print("People Names in Session (Assign Items):", people_names)

    if request.method == "POST":
        # Initialize assignments with empty lists for each person
        assignments = {name: {"items": [], "shared": []} for name in people_names}

        for key, values in request.form.lists():
            if key.startswith("item_"):
                item_index = int(key.split("_")[1].replace("[]", ""))
                
                # Get full item details (name & price)
                item_details = parsed_data["items"][item_index]

                if len(values) > 1:  # If multiple people are assigned (shared item)
                    for person in values:
                        assignments[person]["shared"].append(item_details)
                else:  # If assigned to only one person
                    assignments[values[0]]["items"].append(item_details)

        # Ensure session is updated with correct assignments
        session["assignments"] = assignments
        session.modified = True

        # Debugging: Print out the updated assignments
        print("Updated Assignments in Session:", session["assignments"])

        return redirect(url_for('results'))

    return render_template("assign_items.html", parsed_data=parsed_data, assignments=assignments, num_people=num_people)


@app.route("/results", methods=["GET", "POST"])
def results():
    parsed_data = session.get("parsed_data", None)
    assignments = session.get("assignments")

    print("Parsed Data in Session (Results):", parsed_data)
    print("Assignments in Session (Results):", assignments)

    if not assignments or not any(person_data["items"] or person_data["shared"] for person_data in assignments.values()):
        flash("Error: No assignments found. Please assign items again.")
        return redirect(url_for('assign_items'))

    individual_totals = {}
    grand_total = 0

    for person, data in assignments.items():
        total = sum(item["price"] for item in data["items"])

        for shared_item in data["shared"]:
            shared_price = shared_item["price"]
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

    # 🔥 Fix rounding issue 🔥
    expected_total = parsed_data["total"]
    rounding_error = round(expected_total - grand_total, 2)

    if rounding_error != 0:
        max_owed_person = max(individual_totals, key=lambda p: individual_totals[p]["total"])
        individual_totals[max_owed_person]["total"] += rounding_error

    session["grand_total"] = sum(person_data["total"] for person_data in individual_totals.values())

    return render_template("results.html", parsed_data=parsed_data, assignments=assignments, individual_totals=individual_totals)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
