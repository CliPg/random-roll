from server import vercel
from server import decorators as dec
from database import table

db = table.db
Student = table.Student

@dec.hot_reload
@vercel.register
def main(response, data):
    # 输入校验：兼容 querystring（字符串）以及 body（字典）
    if not isinstance(data, dict):
        response.send_code(200)
        response.send_json({"code": 400, "msg": "Input data must be a dictionary.", "data": []})
        return

    description = data.get("description")
    if not description:
        response.send_code(200)
        response.send_json({"code": 400, "msg": "Input data must contain 'description' field.", "data": []})
        return

    # 解析 order（可能为字符串）
    try:
        order = int(data.get("order", 0))
    except Exception:
        response.send_code(200)
        response.send_json({"code": 400, "msg": "Order must be 0 (升序) or 1 (降序).", "data": []})
        return
    if order not in (0, 1):
        response.send_code(200)
        response.send_json({"code": 400, "msg": "Order must be 0 (升序) or 1 (降序).", "data": []})
        return

    # 解析 num（可能为字符串），-1 表示全部
    try:
        amount = int(data.get("num", -1))
    except Exception:
        response.send_code(200)
        response.send_json({"code": 400, "msg": "Amount must be -1 (all) or a positive integer.", "data": []})
        return
    if not (amount == -1 or amount > 0):
        response.send_code(200)
        response.send_json({"code": 400, "msg": "Amount must be -1 (all) or a positive integer.", "data": []})
        return

    class_desc = description

    db.connect(reuse_if_open=True)
    students_query = Student.select().where(Student.description == class_desc)
    # 先按分数排序，再限制条数（保持语义）
    if order == 0:
        students_query = students_query.order_by(Student.credits.asc())
    else:
        students_query = students_query.order_by(Student.credits.desc())
    if amount != -1:
        students_query = students_query.limit(amount)

    result = []
    for student in students_query:
        result.append({
            "student_id": student.id,
            "student_name": student.name,
            "credits": student.credits,
            "random_rolls": student.rolled,
        })

    db.close()
    response.send_code(200)
    response.send_json({
        "code": 0,
        "msg": "Success" if result else f"No students found for class '{class_desc}'.",
        "data": result
    })