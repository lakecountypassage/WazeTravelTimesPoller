import logging

import helper


class DeletedRoutes:

    def __init__(self, db, rl) -> None:
        super().__init__()
        self.database_conn = db
        self.live_route_list = rl
        self.db_route_list = None
        self.match_list = None

    def run(self):
        self.db_route_list = self.get_route_list()
        self.match_list = self.no_matches(self.live_route_list, self.db_route_list)

        if len(self.match_list[1]) > 0:
            self.update_db()
        else:
            logging.info('No deleted routes')

    def get_route_list(self):
        l = []
        for route in self.get_database_routes():
            l.append(route[0])

        return l

    def get_database_routes(self):
        sql_routes = """SELECT route_id FROM routes WHERE deleted = 0 or deleted is null"""

        c = self.database_conn.cursor()
        c.execute(helper.sql_format(sql_routes))
        r = c.fetchall()

        return r

    def no_matches(self, a, b):
        return [[x for x in a if x not in b], [x for x in b if x not in a]]

    def update_db(self):
        deleted_list = tuple(self.match_list[1])

        sql_update = """UPDATE routes SET deleted = 1 WHERE route_id = ?"""

        c = self.database_conn.cursor()
        for route in deleted_list:
            logging.info(f"Route {route} is deleted, marking it in the database")
            c.execute(helper.sql_format(sql_update), (route,))

    def get_deleted_routes(self):
        sql_routes = """SELECT route_id FROM routes WHERE deleted = 1"""

        c = self.database_conn.cursor()
        c.execute(helper.sql_format(sql_routes))
        r = c.fetchall()

        l = []
        for id in r:
            l.append(id[0])

        return l


if __name__ == '__main__':
    pass
