import random
from System.models import Taskset


def create():
    num = random.randint(1, 60)
    Task = []
    for i in range(num):
        weight = random.randint(1, 200)
        p_num = 10
        while p_num >= 5:
            p_num=random.randint(0, len(Task))
        pred = random.sample(Task, p_num)
        if len(pred) == 0:
            Task.append({"name": "T" + str(i + 1), "pred": None, "weight": weight})
        else:
            t_pred = ""
            for x in range(len(pred)):
                if x == 0:
                    t_pred = t_pred + pred[x]["name"]
                else:
                    t_pred = t_pred + "," + pred[x]["name"]
            Task.append({"name": 'T' + str(i + 1), "pred": t_pred, "weight": weight})
    return str({"Task": Task})
