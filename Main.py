from locust import HttpLocust, TaskSet, task, TaskSequence, seq_task
from random import randint
import pydevd


class SimpleGenericBehaviour(TaskSet):

    def __init__(self, parent):
        super().__init__(parent)
        self.user_ids = []
        self.item_ids = []
        self.ord_ids = []

    # Users
    @task
    def user_create(self):
        resp = self.client.post("/users/create", {"name": "mihai"})
        json_resp = resp.json()

        self.user_ids.append(json_resp["userId"])

    @task
    def user_credit_add(self):
        if len(self.user_ids) < 1:
            return

        resp = self.client.post("/users/credit/add/" + self.get_rand_user_id() + "/" + str(randint(1, 100)),
                                name="/users/credit/add/")

    @task
    def user_credit_add(self):
        if len(self.user_ids) < 1:
            return

        resp = self.client.get("/users/credit/" + self.get_rand_user_id(), name="/users/credit")

    @task
    def user_delete(self):
        if len(self.user_ids) < 1:
            return

        user_id = self.get_rand_user_id()
        resp = self.client.delete("/users/remove/" + user_id, name="/users/remove")

        self.user_ids.remove(user_id)

    @task
    def user_find(self):
        if len(self.user_ids) < 1:
            return
        resp = self.client.get("/users/find/" + self.get_rand_user_id(), name="/users/find")

    # Stock
    @task
    def stock_create(self):
        resp = self.client.post("/stock/item/create", name="/stock/item/create")

        json_resp = resp.json()

        self.item_ids.append(json_resp["itemId"])
        # pydevd.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)

    @task
    def stock_availability(self):
        if len(self.item_ids) < 1:
            return

        resp = self.client.get("/stock/availability/" + self.get_rand_item_id(), name="/stock/item/availability")

    @task
    def stock_add(self):
        if len(self.item_ids) < 1:
            return

        resp = self.client.post("/stock/add/" + self.get_rand_item_id() + "/" + str(randint(1, 100)), name="/stock/add")

    # ORDERS
    @task
    def orders_create(self):
        if len(self.user_ids) < 1:
            return

        resp = self.client.post("/orders/create/" + self.get_rand_user_id(), name="/orders/create")
        json = resp.json()

        self.ord_ids.append(json["orderId"])

    @task
    def orders_add_item(self):
        if len(self.item_ids) < 1 or len(self.ord_ids) < 1:
            return

        resp = self.client.post("/orders/additem/" + self.get_rand_ord_id() + "/" + self.get_rand_item_id(),
                                name="/orders/additem")

    @task
    def orders_find(self):
        if len(self.ord_ids) < 1:
            return

        resp = self.client.get("/orders/find/" + self.get_rand_ord_id(), name="/orders/find")

    @task
    def orders_remove_item(self):
        if len(self.ord_ids) < 1:
            return

        resp = self.client.get("/orders/find/" + self.get_rand_ord_id())
        json_resp = resp.json()

        if len(json_resp) < 1 or len(json_resp["orderItems"]) < 1:
            return

        order_items_keys = list(json_resp["orderItems"].keys())

        arr_len = len(order_items_keys) - 1

        if arr_len == 0:
            self.client.post("/orders/removeitem/" + order_items_keys[0])
        else:
            resp = self.client.post("/orders/removeitem/" + order_items_keys[randint(0, arr_len)])

    @task
    def orders_checkout(self):
        if len(self.ord_ids) < 1:
            return

        resp = self.client.post("/orders/checkout/" + self.get_rand_ord_id(), name="/orders/checkout")

    # Payment

    @task
    def payment_status(self):
        if len(self.ord_ids) < 1:
            return

        resp = self.client.get("/payment/status/" + self.get_rand_ord_id(), name="/payment/status")

    # Helpers
    def get_rand_item_id(self):

        arr_len = len(self.item_ids) - 1

        if arr_len == 0:
            return self.item_ids[0]

        return self.item_ids[randint(0, arr_len)]

    def get_rand_user_id(self):
        arr_len = len(self.user_ids) - 1

        if arr_len == 0:
            return self.user_ids[0]

        return self.user_ids[randint(0, arr_len)]

    def get_rand_ord_id(self):
        arr_len = len(self.ord_ids) - 1

        if arr_len == 0:
            return self.ord_ids[0]

        return self.ord_ids[randint(0, arr_len)]


class GenericWebsiteUser(HttpLocust):
    task_set = SimpleGenericBehaviour
    # host = 'http://localhost:8000/redis'
    min_wait = 1000
    max_wait = 3000

# class RedisWebsiteUser(GenericWebsiteUser):
#     host = GenericWebsiteUser.host + 'redis/'
#
#
# class SqlWebsiteUser(HttpLocust):
#     host = GenericWebsiteUser.host + 'sql/'
