from server import vercel
from server import decorators as dec
from database import table
import importlib
from user.login import get_unionid_from_code

db = table.db
Student = table.Student
ClassCreater = table.ClassCreater
# 导入标准库 random，避免与本文件名冲突
_stdlib_random = importlib.import_module("random")


@dec.hot_reload
@vercel.register
def main(response, data):
    assert "Authorization" in response.headers, "Missing 'Authorization' header."
    assert isinstance(data, dict), "Input data must be a dictionary."
    assert "description" in data, "Input data must contain 'description' field."

    token_code = response.headers["Authorization"]
    token = get_unionid_from_code(token_code)
    if not token:
        response.send_code(200)
        response.send_json({
            "code": 401,
            "msg": "Invalid or expired Weixin code, please re-login.",
            "data": {}
        })
        return
    desc = data["description"]

    db.connect(reuse_if_open=True)
    klass = ClassCreater.get_or_none((ClassCreater.description == desc) &
                                     (ClassCreater.creator == token))
    if not klass:
        response.send_code(200)
        response.send_json({
            "code": 403,
            "msg": "Unauthorized: Invalid token or class description.",
            "data": {

            }})
        db.close()
        return
    
    # 获取该班级描述下的所有学生和分数
    student_score = []
    query = Student.select().where(Student.description == desc)
    for student in query:
        student_score.append({
            "id": student.id,
            "name": student.name,
            "credits": student.credits,
        })
    db.close()

    # 随机选一个（使用标准库 random，避免与模块名冲突）
    if not student_score:
        response.send_code(200)
        response.send_json({
            "code": 200,
            "msg": "No students found for this class.",
            "data": {}
        })
        return

    picked = _stdlib_random.choice(student_score)

    response.send_code(200)
    response.send_json({
        "code": 200,
        "msg": "Class data retrieved successfully.",
        "data": {
            "student_id": picked["id"],
            "student_name": picked["name"],
        }
    })