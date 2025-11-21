from server import vercel
from server import decorators as dec
from database import table
from user.login import get_unionid_from_code

db = table.db
Student = table.Student
ClassCreator = table.ClassCreater


@dec.hot_reload
@vercel.register
def main(response, data, headers):
    """Return all classes (and their students) for the current authenticated user.
    Expects Authorization header with Weixin js_code. Returns JSON:
    { code:0, msg:'Success', data: [ { description:..., students: [...] }, ... ] }
    """
    assert "Authorization" in headers, "Missing 'Authorization' header."

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

    db.connect(reuse_if_open=True)
    classes = ClassCreator.select().where(ClassCreator.creator == unionid)
    result = []
    for klass in classes:
        students = []
        for s in Student.select().where(Student.description == klass.description):
            students.append({
                "student_id": s.id,
                "student_name": s.name,
                "student_major": s.major,
                "credits": s.credits,
                "random_rolls": s.rolled,
                "description": s.description
            })
        result.append({
            "description": klass.description,
            "students": students
        })
    db.close()

    response.send_code(200)
    response.send_json({
        "code": 0,
        "msg": "Success",
        "data": result
    })
