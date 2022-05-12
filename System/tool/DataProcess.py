import networkx as nx
import json


def process_res(G, long_list):
    res = []
    i = 1
    for list1 in long_list:
        res_temp = []
        for x in list1:
            temp = {"name": x, "start_time": G.nodes.get(x)['start_time'], "end_time": G.nodes.get(x)['end_time']}
            res_temp.append(temp)
        t_dic = {"machine": i, "task": res_temp}
        res.append(t_dic)
        i = i + 1

    return res


def is_json(context):
    try:
        json.loads(context)
    except Exception as e:
        return False
    return True


# 将json文件内容转化成DAG图
def trans_Json(context):
    G = nx.DiGraph()
    if is_json(context):
        x = json.loads(context)
        for y in x["Task"]:
            G.add_node(y["name"], weight=y["weight"], start_time=0, end_time=0)
            if y["pred"] is not None:
                pred = y["pred"].split(',')
                for i in pred:
                    G.add_edge(i, y['name'])
        return G
    else:
        return None


# 计算每个任务的高度
def height_num(G, node):
    if len(list(G.predecessors(node))) == 0:
        return 0
    else:
        list1 = []
        for i in list(G.predecessors(node)):
            list1.append(height_num(G, i))
        return max(list1) + 1


# 处理DAG图
def process_dag(G):
    h = []
    H = []
    nodes = list(G.nodes)
    for node in nodes:
        h.append(height_num(G, node))
    total = max(h) + 1
    for i in range(total):
        temp = []
        for j in range(len(h)):
            if h[j] == i:
                temp.append(nodes[j])
        H.append(temp)
    return H


# 将需要训练的数据转化成树的形式
def trans_to_tree(G):
    H = process_dag(G)
    result = []
    for layer in H:
        res = []
        for one in layer:
            temp = {"name": one, "weight": G.nodes.get(one)['weight'],"suc":list(G.successors(one))}
            res.append(temp)
        result.append(res)
    return {"result": result}
