from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Cấu hình quy định mặc định
config = {
    "max_children": 25,
    "base_tuition": 1500000,
    "meal_fee_per_day": 25000
}

# Cơ sở dữ liệu tạm thời
children_db = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/children', methods=['GET', 'POST'])
def manage_children():
    if request.method == 'POST':
        if len(children_db) >= config["max_children"]:
            return jsonify({"success": False, "message": f"Lớp đã đạt sĩ số tối đa ({config['max_children']} trẻ)."}), 400
        data = request.json
        new_child = {
            "id": len(children_db) + 1,
            "name": data.get("name"),
            "dob": data.get("dob"),
            "gender": data.get("gender"),
            "parent": data.get("parent"),
            "phone": data.get("phone")
        }
        children_db.append(new_child)
        return jsonify({"success": True, "message": "Thêm trẻ thành công!", "data": new_child})
    return jsonify({"children": children_db, "max_capacity": config["max_children"]})

@app.route('/api/health', methods=['POST'])
def record_health():
    data = request.json
    temp = float(data.get("temperature", 0))
    is_fever = temp > 37.5
    alert_message = "⚠️ CẢNH BÁO: Trẻ có dấu hiệu SỐT!" if is_fever else "Sức khỏe bình thường."
    return jsonify({"success": True, "is_fever": is_fever, "message": alert_message})

@app.route('/api/tuition/calculate', methods=['POST'])
def calculate_tuition():
    data = request.json
    meal_days = int(data.get("meal_days", 0))
    child_id = int(data.get("child_id", 0))
    child = next((c for c in children_db if c["id"] == child_id), None)
    if not child:
        return jsonify({"success": False, "message": "Không tìm thấy trẻ!"}), 404
    total_meal_fee = meal_days * config["meal_fee_per_day"]
    total_amount = config["base_tuition"] + total_meal_fee
    return jsonify({
        "success": True,
        "invoice": {
            "child_name": child["name"],
            "base_tuition": config["base_tuition"],
            "meal_days": meal_days,
            "total_meal_fee": total_meal_fee,
            "total_amount": total_amount
        }
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    male_count = sum(1 for c in children_db if c["gender"] == "Nam")
    female_count = sum(1 for c in children_db if c["gender"] == "Nữ")
    return jsonify({"total_students": len(children_db), "max_capacity": config["max_children"], "male_count": male_count, "female_count": female_count})

if __name__ == '__main__':
    app.run(debug=True, port=5000)