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

    token_code = headers["Authorization"]
    unionid = get_unionid_from_code(token_code)
    if not unionid:
        response.send_code(200)
        response.send_json({
            "code": 401,
            "msg": "Invalid or expired Weixin code, please re-login.",
        })
        return

    db.connect(reuse_if_open=True)
    # find all classes created by this user
    classes = list(ClassCreator.select().where(ClassCreator.creator == unionid))
    if not classes:
        db.close()
        response.send_code(200)
        response.send_json({
            "code": 0,
            "msg": "No classes to delete.",
            "deleted_classes": 0,
            "deleted_students": 0,
            "deleted_score_mods": 0
        })
        return

    descriptions = [c.description for c in classes]
    deleted_classes = 0
    deleted_students = 0
    deleted_score_mods = 0
    try:
        with db.atomic():
            # delete students
            deleted_students = Student.delete().where(Student.description.in_(descriptions)).execute()
            # delete score modifications
            deleted_score_mods = ScoreModify.delete().where(ScoreModify.description.in_(descriptions)).execute()
            # delete class entries
            deleted_classes = ClassCreator.delete().where(ClassCreator.description.in_(descriptions)).execute()
    except Exception as e:
        db.close()
        response.send_code(200)
        response.send_json({
            "code": 500,
            "msg": f"Deletion failed: {str(e)}",
        })
        return

    db.close()
    response.send_code(200)
    response.send_json({
        "code": 0,
        "msg": "All classes and related data deleted successfully.",
        "deleted_classes": deleted_classes,
        "deleted_students": deleted_students,
        "deleted_score_mods": deleted_score_mods
    })
