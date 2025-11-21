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
    assert "Authorization" in headers, "Missing Authorization header."
    assert isinstance(data, dict), "Input data must be a dictionary."
    assert "description" in data, "Input data must contain 'description' field."
    assert "students" in data, "Input data must contain 'students' field."
    for item in data["students"]:
        # basic validations
        assert isinstance(item, dict), "Each student record must be a dictionary."
        for k in ("student_id", "student_name", "student_major"):
            assert k in item, f"Each student record must have '{k}' field."
        sid = item["student_id"]
        name = item["student_name"]
        major = item["student_major"]
        # more validations: non-empty strings and integer grade
        assert isinstance(sid, str) and sid.strip() != "", "student_id must be a non-empty string"
        assert isinstance(name, str) and name.strip() != "", "student_name must be a non-empty string"
        assert isinstance(major, str) and major.strip() != "", "student_major must be a non-empty string"

    db.connect(reuse_if_open=True)

    inserted = 0
    updated = 0

    token_code = headers["Authorization"]
    # exchange code for unionid/openid; require successful exchange
    unionid = get_unionid_from_code(token_code)
    if not unionid:
        response.send_code(200)
        response.send_json({
            "code": 401,
            "msg": "Invalid or expired Weixin code, please re-login.",
        })
        db.close()
        return
    description = data["description"]
    klass = classCreator.get_or_none(classCreator.description == description)
    if not klass:
        classCreator.create(description=description, creator=unionid)

    for item in data["students"]:
        sid = item["student_id"]
        name = item["student_name"]
        major = item["student_major"]

        # upsert: if exists update, otherwise create
        # and the description must as same as provided description
        existing: Student = Student.get_or_none((Student.id == sid) &
                                                (Student.description == description))
        if existing:
            # update fields
            existing.name = name
            existing.major = major
            existing.save()
            updated += 1
        else:
            Student.create(id=sid, name=name, major=major, 
                           description=description)
            inserted += 1

    db.close()

    # return a concise summary
    response.send_code(200)
    response.send_json({
        "code": 200,
        "msg": "Import completed successfully.",
        "inserted": inserted,
        "updated": updated
    })