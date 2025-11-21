from server import vercel
from server import decorators as dec
from database import table
from user.login import get_unionid_from_code

db = table.db
Student = table.Student
classCreator = table.ClassCreater

@dec.hot_reload
@vercel.register
def main(response, data, headers):
    assert "Authorization" in headers, "Missing 'Authorization' header."
    assert isinstance(data, dict), "Input data must be a dictionary."
    assert "description" in data, "Input data must contain 'description' field."

    token_code = headers["Authorization"]
    unionid = get_unionid_from_code(token_code)
    if not unionid:
        response.send_code(200)
        response.send_json({
            "code": 401,
            "msg": "Invalid or expired Weixin code, please re-login.",
            "data": []
        })
        return
    class_desc = data["description"]

    db.connect(reuse_if_open=True)
    klass: classCreator = classCreator.get_or_none(classCreator.description == class_desc)
    if not klass:
        response.send_code(200)
        response.send_json({
            "code": 404,
            "msg": f"Class with description '{class_desc}' not found.",
            "data": []
        })
        db.close()
        return
    if klass.creator != unionid:
        response.send_code(200)
        response.send_json({
            "code": 403,
            "msg": "Invalid authentication token.",
            "data": []
        })
        db.close()
        return
    
    student_menu = []
    for student in Student.select().where(Student.description == class_desc):
        student_menu.append({
            "id": student.id,
            "student_id": student.id,
            "student_name": student.name,
            "student_major": student.major,
            "credits": student.credits,
            "random_rolls": student.rolled,
            "description": student.description
        })


    response.send_code(200)
    response.send_json({
        "code": 0,
        "msg": "Success",
        "data": student_menu
    })