# Copyright 2015-2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file
# except in compliance with the License. A copy of the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS"
# BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under the License.

import os
import string
from random import randint
from locust import HttpLocust, TaskSet, task, TaskSequence, seq_task


class MyTaskSet(TaskSequence):
    # def __init__(self, parent):
    #     super().__init__(parent)
    #     self.order_ids = []
    #     self.user_id = None
    #     self.item_ids = []

    item_ids = []
    order_ids = []
    user_id = None

    @seq_task(1)
    def index(self):
        # response = self.client.get("/")
        resp = self.client.post("/users/create", json={"name": "mihai"})
        json = resp.json()
        self.user_id = json["userId"]

    @seq_task(2)
    @task(10)
    def populate_stock(self):
        resp = self.client.post("/stock/item/create", json={"price": 1})
        json_resp = resp.json()

        item_id = json_resp["itemId"]
        resp = self.client.post("/stock/add/{0}/{1}".format(item_id, str(1000000)), name="/stock/add")

        self.item_ids.append(item_id)

    @seq_task(3)
    def user_credit_add(self, amt=20):
        resp = self.client.post("/users/credit/add/{0}/{1}".format(self.user_id, str(amt)),
                                name="/users/credit/add/")

    @seq_task(4)
    def stock_availability(self):
        resp = self.client.get("/stock/availability/" + str(get_rand_item_id(self.item_ids)),
                               name="/stock/item/availability")

    @seq_task(5)
    @task(10)
    def orders_create(self):
        resp = self.client.post("/orders/create/" + str(self.user_id), name="/orders/create")
        json = resp.json()

        self.order_ids.append(json["orderId"])

    @seq_task(6)
    @task(5)
    def orders_remove(self):
        ord_id = get_rand_ord_id(self.order_ids)
        self.order_ids.remove(ord_id)
        resp = self.client.delete("/orders/remove/" + str(ord_id), name="/orders/remove")

    @seq_task(7)
    @task(10)
    def orders_add_item(self):
        resp = self.client.post("/orders/addItem/{0}/{1}".format(get_rand_ord_id(self.order_ids),
                                                                 get_rand_item_id(self.item_ids)),
                                name="/orders/addItem")

    @seq_task(8)
    @task(4)
    def orders_remove_item(self):
        ord_id = get_rand_ord_id(self.order_ids)

        resp = self.client.get("/orders/find/" + str(ord_id), name="/orders/find/")
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

    @seq_task(9)
    @task(5)
    def orders_checkout(self):
        ord_id = get_rand_ord_id(self.order_ids)
        self.order_ids.remove(ord_id)

        resp = self.client.post("/orders/checkout/" + str(ord_id), name="/orders/checkout")

    # This task will 15 times for every 1000 runs of the above task
    # @task(15)
    # def about(self):
    #     self.client.get("/blog")

    # This task will run once for every 1000 runs of the above task
    # @task(1)
    # def about(self):
    #     id = id_generator()
    #     self.client.post("/signup", {"email": "example@example.com", "name": "Test"})


class MyLocust(HttpLocust):
    # host = os.getenv('TARGET_URL', "http://localhost")
    host = "http://18.130.71.115:8000/redis"
    # host = host.replace("redis", "sql")
    task_set = MyTaskSet
    min_wait = 1000
    max_wait = 1500


def get_rand_ord_id(ord_ids):
    arr_len = len(ord_ids) - 1

    if arr_len == 0:
        return ord_ids[0]

    return ord_ids[randint(0, arr_len)]


def get_rand_item_id(item_ids):
    arr_len = len(item_ids) - 1

    if arr_len == 0:
        return item_ids[0]

    return item_ids[randint(0, arr_len)]
