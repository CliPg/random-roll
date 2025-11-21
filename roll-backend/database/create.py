import os
import table


def ensure_db_and_table():
    """Ensure database file exists and the `student` table is created with required schema."""
    need_create_file = not os.path.exists(table.DB_PATH)

    # connect (this will create the sqlite file on disk when tables are created)
    table.db.connect(reuse_if_open=True)

    if need_create_file:
        # Create tables which will also create the sqlite file
        table.db.create_tables([table.Student, table.ClassCreater, table.ScoreModify])
        print(f"Created database file '{table.DB_PATH}' and 'student' table.")
    else:
        # If file exists, ensure table exists; create if missing
        if not table.db.table_exists(table.Student._meta.table_name):
            table.db.create_tables([table.Student])
            print(f"Database file exists; created missing 'student' table in '{table.DB_PATH}'.")
        else:
            print(f"Database file '{table.DB_PATH}' and table 'student' already exist.")

    table.db.close()


if __name__ == "__main__":
    ensure_db_and_table()
