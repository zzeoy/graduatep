import queue
from System.tool.DataProcess import process_res, trans_Json
from System.tool.Tools import cal, next_p, pred_empty_num, add_arrange
from System.tool.Unit import context2


def next_P2(list1, M, G):
    time = cal(list1, G, M)
    p = time.index(min(time))
    return p


def is_pred_in(G, node):
    pred = list(G.predecessors(node))
    for i in pred:
        if G.nodes.get(i)['arrange'] == 0:
            return False
    return True


def schedule(G, list1, p, qe, M):
    if qe.empty():
        return
    node = qe.get()
    list1[p].append(node)
    p = next_P2(list1, M, G)
    sus = list(G.successors(node))
    if len(sus) == 0:
        schedule(G, list1, p, qe, M)
    else:
        sus_temp = []
        for j in sus:
            dic = {'name': j, 'weight': G.nodes.get(j)['weight']}
            sus_temp.append(dic)
        sus_temp.sort(key=lambda x: x['weight'])
        for i in sus_temp:
            if G.nodes.get(i['name'])['arrange'] == 0 and is_pred_in(G, i['name']):
                qe.put(i['name'])
                G.nodes.get(i['name'])['arrange'] = 1
        schedule(G, list1, p, qe, M)


def TA(G, M):
    num, emptyPre = pred_empty_num(G)
    if num >= 1:
        G.add_node("Start", weight=0)
        for name in emptyPre:
            G.add_edge("Start", name)
        start_node = "Start"
    else:
        start_node = emptyPre[0]
    # 初始化G的arrange属性
    G = add_arrange(G)
    p = 0
    machine = []
    for i in range(M):
        sub_machine = []
        machine.append(sub_machine)
    # 初始化队列
    qe = queue.Queue()
    G.nodes.get(start_node)['arrange'] = 1
    qe.put(start_node)
    schedule(G, machine, p, qe, M)
    if num >= 1:
        G.remove_node("Start")
        machine[0].pop(0)
    time = max(cal(machine, G, M))
    machine = process_res(G, machine)
    return machine, time
