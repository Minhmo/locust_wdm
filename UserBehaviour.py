from locust import HttpLocust, TaskSet, task, TaskSequence, seq_task
from random import randint
import requests


class SingleUserBehaviour(TaskSequence):

    def __init__(self, parent):
        super().__init__(parent)
        self.order_ids = []
        self.user_id = None
        # self.item_ids = []

    def on_start(self):
        self.user_id = user_create(self)

    @seq_task(1)
    def user_credit_add(self, amt=20):
        resp = self.client.post("/users/credit/add/{0}/{1}".format(self.user_id, str(amt)),
                                name="/users/credit/add/")

    # @task
    # def stock_availability(self):
    #     resp = self.client.get("/stock/availability/" + get_rand_item_id(), name="/stock/item/availability")

    @seq_task(2)
    @task(10)
    def orders_create(self):
        resp = self.client.post("/orders/create/" + self.user_id, name="/orders/create")
        json = resp.json()

        self.order_ids.append(json["orderId"])

    @seq_task(3)
    @task(5)
    def orders_remove(self):
        ord_id = get_rand_ord_id(self.order_ids)
        resp = self.client.delete("/orders/remove/" + ord_id, name="/orders/remove")

        self.order_ids.remove(ord_id)

    @seq_task(4)
    @task(10)
    def orders_add_item(self):
        resp = self.client.post("/orders/addItem/{0}/{1}".format(get_rand_ord_id(self.order_ids),
                                                                 get_rand_item_id()),
                                name="/orders/addItem")

    @seq_task(5)
    @task(4)
    def orders_remove_item(self):
        ord_id = get_rand_ord_id(self.order_ids)

        resp = self.client.get("/orders/find/" + ord_id, name="/orders/find/")
        json_resp = resp.json()

        order_items_keys = list(json_resp["orderItems"].keys())

        if len(order_items_keys) == 0:
            return

        arr_len = len(order_items_keys) - 1

        if arr_len == 0:
            self.client.delete("/orders/removeItem/{0}/{1}".format(ord_id, order_items_keys[0]),
                               name="/orders/removeItem/")
        else:
            self.client.delete("/orders/removeItem/{0}/{1}".format(ord_id, order_items_keys[randint(0, arr_len)]),
                               name="/orders/removeItem/")

    @seq_task(6)
    def orders_checkout(self):
        for ord_id in self.order_ids:
            resp = self.client.post("/orders/checkout/" + ord_id, name="/orders/checkout")

        self.order_ids = []


class SequenceWebsiteUser(HttpLocust):
    task_set = SingleUserBehaviour
    # host = 'http://localhost:8000/redis'
    min_wait = 1000
    max_wait = 3000

    def setup(self):
        populate_stock(self.host)


item_ids = []


def populate_stock(host, items=500):
    for i in range(items):
        resp = requests.post(host + "/stock/item/create", {"price": 1})
        json_resp = resp.json()

        item_id = json_resp["itemId"]
        item_ids.append(item_id)

        resp = requests.post(host + "/stock/add/{0}/{1}".format(item_id, str(1000000)))

    # return item_ids


def user_create(l):
    resp = l.client.post("/users/create", {"name": "mihai"})
    json_resp = resp.json()
    return json_resp["userId"]


def get_rand_ord_id(ord_ids):
    arr_len = len(ord_ids) - 1

    if arr_len == 0:
        return ord_ids[0]

    return ord_ids[randint(0, arr_len)]


def get_rand_item_id():
    arr_len = len(item_ids) - 1

    if arr_len == 0:
        return item_ids[0]

    return item_ids[randint(0, arr_len)]
