from locust import HttpLocust, TaskSet, task, TaskSequence, seq_task
from random import randint
import pydevd


class SimpleRedisBehaviour(TaskSet):
    user_ids = []
    item_ids = []
    ord_ids = []

    @task
    def user_create(self):
        resp = self.client.post("/users/create")
        json_resp = resp.json()

        self.user_ids.append(json_resp["id"])

        # pydevd.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)

    @task
    def stock_create(self):
        resp = self.client.post("/stock/item/create")

        json_resp = resp.json()

        self.item_ids.append(json_resp["id"])
        # pydevd.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)

    @task
    def stock_availability(self):
        if len(self.item_ids) < 1:
            pass

        resp = self.client.get("/stock/availability/" + self.get_rand_item_id())

    @task
    def stock_add(self):
        if len(self.item_ids) < 1:
            pass

        resp = self.client.post("/stock/add/" + self.get_rand_item_id() + "/" + randint(1, 100))

    # ORDERS
    @task
    def orders_create(self):
        if len(self.user_ids) < 1:
            pass

        resp = self.client.post("/orders/create/" + self.get_rand_user_id())
        json = resp.json()

        self.ord_ids.append(json["id"])

    @task
    def orders_add_item(self):
        if len(self.item_ids) < 1 or len(self.ord_ids) < 1:
            pass

        resp = self.client.post("/orders/additem/" + self.get_rand_ord_id() + "/" + self.get_rand_item_id())

    @task
    def orders_remove_item(self):
        if len(self.item_ids) < 1 or len(self.ord_ids) < 1:
            pass

        resp = self.client.post("/orders/removeitem/" + self.get_rand_ord_id() + "/" + self.get_rand_item_id())

    # Helpers
    def get_rand_item_id(self):
        return self.item_ids[randint(0, len(self.item_ids) - 1)]

    def get_rand_user_id(self):
        return self.user_ids[randint(0, len(self.user_ids) - 1)]

    def get_rand_ord_id(self):
        return self.ord_ids[randint(0, len(self.ord_ids) - 1)]


class WebsiteUser(HttpLocust):
    task_set = SimpleRedisBehaviour
    host = 'http://localhost:8000/redis'
    min_wait = 1000
    max_wait = 3000
