import logging

import helper


class DeletedRoutes:

    def __init__(self, db, rl) -> None:
        super().__init__()
        self.database_conn = db
        self.live_route_list = rl
        self.db_route_list = None
        self.match_list = None

    def run(self, use_postgres):
        self.db_route_list = self.get_route_list(use_postgres)
        self.match_list = self.no_matches(self.live_route_list, self.db_route_list)

        if len(self.match_list[1]) > 0:
            self.update_db(use_postgres)
        else:
            logging.info('No deleted routes')

    def get_route_list(self, use_postgres):
        routes = []
        for route in self.get_database_routes(use_postgres):
            routes.append(str(route[0]))

        return routes

    def get_database_routes(self, use_postgres):
        sql_routes = """SELECT route_id FROM routes WHERE deleted = 0 or deleted is null"""

        c = self.database_conn.cursor()
        c.execute(helper.sql_format(sql_routes, use_postgres))
        r = c.fetchall()

        return r

    @staticmethod
    def no_matches(a, b):
        return [[x for x in a if x not in b], [x for x in b if x not in a]]

    def update_db(self, use_postgres):
        deleted_list = tuple(self.match_list[1])

        sql_update = """UPDATE routes SET deleted = 1 WHERE route_id = ?"""

        c = self.database_conn.cursor()
        for route in deleted_list:
            logging.info(f"Route {route} is deleted, marking it in the database")
            c.execute(helper.sql_format(sql_update, use_postgres), (route,))

    def get_deleted_routes(self, use_postgres):
        sql_routes = """SELECT route_id FROM routes WHERE deleted = 1"""

        c = self.database_conn.cursor()
        c.execute(helper.sql_format(sql_routes, use_postgres))
        r = c.fetchall()

        routes = []
        for ids in r:
            routes.append(ids[0])

        return routes


if __name__ == '__main__':
    pass
