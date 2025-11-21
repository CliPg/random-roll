from server import vercel
from server import decorators as dec
from database import table
from user.login import get_unionid_from_code

db = table.db
Student = table.Student
ScoreModify = table.ScoreModify
ClassCreator = table.ClassCreater

@dec.hot_reload
@vercel.register
def main(response, data, headers):
    assert response.method == "DELETE", "Method Not Allowed, only DELETE is allowed."
    assert "Authorization" in headers, "Missing Authorization header."
    assert isinstance(data, dict), "Invalid data format, expected a dictionary."
    assert "description" in data, "Missing 'description' in request data."

    token_code = headers["Authorization"]
    unionid = get_unionid_from_code(token_code)
    if not unionid:
        response.send_code(200)
        response.send_json({
            "code": 401,
            "msg": "Invalid or expired Weixin code, please re-login.",
        })
        return
    class_desc = data["description"]

    db.connect(reuse_if_open=True)
    klass: ClassCreator = ClassCreator.get_or_none(ClassCreator.description == class_desc)
    if not klass:
        response.send_code(200)
        response.send_json({
            "code": 404,
            "msg": f"Class with description '{class_desc}' not found.",
        })
        db.close()
        return
    if klass.creator != unionid:
        response.send_code(200)
        response.send_json({
            "code": 403,
            "msg": "Invalid authentication token.",
        })
        db.close()
        return
    
    with db.atomic():
        # Delete all students associated with the class
        Student.delete().where(Student.description == class_desc).execute()
        # Delete the class itself
        klass.delete_instance()
        # Delete all score modifications associated with the class
        ScoreModify.delete().where(ScoreModify.description == class_desc).execute()
    db.close()

    response.send_code(200)
    response.send_json({
        "code": 200,
        "msg": f"Class '{class_desc}' and all associated students have been deleted successfully.",
    })