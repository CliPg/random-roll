from server import vercel
from server import decorators as dec
from database import table

import datetime

db = table.db
Student = table.Student
ScoreModify = table.ScoreModify


def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calc_score(is_attend, is_repeat, answer_condition):
    score = 0
    # 每点到一次且到达课堂，则积分+1
    if is_attend:
        score += 1
    else:
        return 0
    # 能复述问题则加0.5分，否则扣1分
    if is_repeat:
        score += 0.5
    else:
        score -= 1
    # 根据回答问题情况评分
    return score + answer_condition


@dec.hot_reload
@vercel.register
def main(response, data):
    assert isinstance(data, dict), "Input data must be a dictionary."
    assert "student_id" in data, "Input data must contain 'student_id' field."
    assert "description" in data, "Input data must contain 'description' field."
    assert "is_attend" in data, "Input data must contain 'is_attend' field."
    assert "is_repeat" in data, "Input data must contain 'is_repeat' field."
    assert "answer_condition" in data, "Input data must contain 'answer_condition' field."

    sid = data["student_id"]
    desc = data["description"]

    # 参数来自 querystring 或 body，可能为字符串，需要做类型转换
    def parse_bool(v):
        if isinstance(v, bool):
            return v
        if v is None:
            return False
        s = str(v).strip().lower()
        if s in ("1", "true", "yes", "y", "t"):
            return True
        if s in ("0", "false", "no", "n", "f"):
            return False
        # 默认：False
        return False

    def parse_number(v):
        if isinstance(v, (int, float)):
            return float(v)
        try:
            return float(str(v))
        except Exception:
            return 0.0

    is_attend = parse_bool(data["is_attend"])
    is_repeat = parse_bool(data["is_repeat"])
    answer_condition = parse_number(data["answer_condition"])

    db.connect(reuse_if_open=True)
    existing: Student = Student.get_or_none((Student.id == sid) &
                                            (Student.description == desc))
    if not existing:
        response.send_code(200)
        response.send_json({
            "code": 404,
            "msg": f"Student with id '{sid}' in class '{desc}' not found.",
            "data": []
        })
        db.close()
        return
    
    # 计算积分变化并更新学生积分
    score_changes = calc_score(is_attend, is_repeat, answer_condition)
    existing.credits += score_changes
    existing.rolled += 1
    existing.save()

    # 记录积分变动
    ScoreModify.create(
        id=sid,
        description=desc,
        time=get_current_time(),
        modify=score_changes,
        is_attend=is_attend,
        is_repeat=is_repeat,
        answer_condition=answer_condition
    )

    response.send_code(200)
    response.send_json({
        "code": 0,
        "msg": f"Score updated successfully, Now credits: {existing.credits}"
    })
    db.close()