import os
from peewee import SqliteDatabase, Model, CharField, IntegerField, BooleanField, CompositeKey


# Database file placed in the same folder as this script
BASE_DIR = os.path.abspath(os.getcwd())
DB_PATH = os.path.join(BASE_DIR, "database.db")

db = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    class Meta:
        database = db


class Student(BaseModel):
    id = CharField()            # 学号
    name = CharField()          # non-null 姓名
    major = CharField()         # non-null 专业
    description = CharField()   # non-null 班级描述，实际上就是班级名称
    credits = IntegerField(default = 0)  # default to 0 积分
    rolled = IntegerField(default = 0)   # default to 0  随机到几次
    class Meta:
        primary_key = CompositeKey('id', 'description')


class ScoreModify(BaseModel):
    id = CharField()            # 学号，需要与上表联立查询
    description = CharField()   # non-null 班级描述，实际上就是班级名称
    time = CharField()          # non-null 修改时间，格式YYYY-MM-DD HH:MM:SS
    modify = IntegerField()     # non-null 加减分值
    is_attend = BooleanField()  # non-null 是否出勤
    is_repeat = BooleanField()  # non-null 是否能复述问题(表示学生有在听课)
    answer_condition = IntegerField()  # non-null 回答问题情况评分
    class Meta:
        primary_key = CompositeKey('id', 'description', 'time')


class ClassCreater(BaseModel):
    description = CharField(primary_key=True)  # 班级描述，实际上就是班级名称
    creator = CharField()  # non-null 创建者姓名，有可能是token