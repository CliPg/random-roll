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
    # Expect Authorization header in the HTTP handler object
    assert hasattr(response, 'headers'), "Missing response headers"
    assert isinstance(data, dict), "Input data must be a dictionary."
    assert "description" in data, "Input data must contain 'description' field."

    token_code = None
    # headers may be available on response (handler) or passed separately
    if hasattr(response, 'headers') and 'Authorization' in response.headers:
        token_code = response.headers['Authorization']
    else:
        # try data-provided header fallback
        token_code = data.get('_auth')

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
    mode = str(data.get('mode', 'random')).lower()

    db.connect(reuse_if_open=True)
    klass = ClassCreater.get_or_none((ClassCreater.description == desc) &
                                     (ClassCreater.creator == token))
    if not klass:
        response.send_code(200)
        response.send_json({
            "code": 403,
            "msg": "Unauthorized: Invalid token or class description.",
            "data": {}
        })
        db.close()
        return

    # Fetch students for the class
    query = Student.select().where(Student.description == desc)
    students = list(query)

    if not students:
        response.send_code(200)
        response.send_json({"code": 0, "msg": "No students found for this class.", "data": {}})
        db.close()
        return

    # Choose based on mode
    if mode == 'order':
        # pick student(s) with minimal 'rolled' count (round-robin fairness)
        min_rolled = min(s.rolled for s in students)
        candidates = [s for s in students if s.rolled == min_rolled]
        # deterministic pick: sort by id then choose first
        candidates.sort(key=lambda s: s.id)
        picked = candidates[0]
    else:
        # weighted random: students with higher credits should have LOWER probability
        # use inverse weighting: weight = 1 / (credits + 1)
        try:
            weights = []
            for s in students:
                try:
                    c = int(s.credits)
                except Exception:
                    c = 0
                weights.append(1.0 / (c + 1))
            # random.choices supports weights
            picked = _stdlib_random.choices(students, weights=weights, k=1)[0]
        except Exception:
            # fallback to uniform random
            picked = _stdlib_random.choice(students)


    db.close()

    response.send_code(200)
    response.send_json({
        "code": 0,
        "msg": "OK",
        "data": {
            "student_id": picked.id,
            "student_name": picked.name,
        }
    })