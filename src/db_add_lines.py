import db_conn

alter_sql = 'ALTER TABLE routes ADD lines TEXT;'
select_sql = 'SELECT EXISTS (SELECT * FROM sqlite_master WHERE tbl_name = "routes" AND sql LIKE "%lines%");'


def alter_table(db):
    print('adding column to routes table')
    c = db.cursor()
    c.execute(alter_sql)
    db.commit()


def get_column(db):
    c = db.cursor()

    c.execute(select_sql)
    r = c.fetchone()

    print(f'column exists: {r[0]}')
    return r[0]


if __name__ == '__main__':
    with db_conn.DatabaseConnection() as db:
        r = get_column(db)
        if r == 0:
            alter_table(db)