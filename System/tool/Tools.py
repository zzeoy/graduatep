from collections import deque


# 判断是否所有队列都计算完
def isempty(list2):
    break_status = True
    for list1 in list2:
        if len(list1) != 0:
            break_status = False
    return break_status


# 判断下一个队列的序号
def next_p(P, M):
    P = (P + 1) % M
    return P


# 是否需要改变该队列的调度时间
def change_time(list_t, time, sus, comp_time):
    time_change = []
    for x in range(len(time)):
        time_change.append(0)
        if len(list_t[x]) != 0:
            temp = list_t[x].popleft()
            list_t[x].appendleft(temp)
            if sus.count(temp) != 0 and time[x] < comp_time:
                time_change[x] = comp_time
    return time_change


# 判断前继节点是否都没了
def pred_empty(G, node):
    if G.nodes.get(node) is None:
        return False
    if len(list(G.predecessors(node))) == 0:
        return True
    else:
        return False


def pred_empty_num(G):
    num = 0
    list1 = []
    for node in list(G.nodes()):
        if pred_empty(G, node):
            num = num + 1
            list1.append(node)
    return num, list1


def add_arrange(G):
    for node in list(G.nodes()):
        G.nodes.get(node)['arrange'] = 0
    return G


# 调度时长的计算个体适应度
def cal(subpopulation, G, M):
    # 计算每个个体的适应度
    G_temp = G.copy()
    time = []
    list_c = []
    for i in range(M):  # 生成m的队列
        time.append(0)
        q = deque()
        for x in subpopulation[i]:
            q.append(x)
        list_c.append(q)
    p = 0
    trys = 0
    while not isempty(list_c):
        trys = trys + 1
        if len(list_c[p]) == 0:
            p = next_p(p, M)
        else:
            temp = list_c[p].popleft()
            if pred_empty(G, temp) is not True:
                for node in list(G.predecessors(temp)):
                    if G.nodes.get(node)['end_time'] > time[p]:
                        time[p] = G.nodes.get(node)['end_time']
            if pred_empty(G_temp, temp):
                G.nodes.get(temp)['start_time'] = time[p]
                time[p] += G_temp.nodes.get(temp)['weight']
                G.nodes.get(temp)['end_time'] = time[p]
                judge = change_time(list_c, time, list(G_temp.successors(temp)), time[p])
                for j in range(len(judge)):
                    if judge[j] != 0:
                        time[j] = judge[j]
                G_temp.remove_node(temp)
            else:
                list_c[p].appendleft(temp)
            p = next_p(p, M)
    return time


def check_single(G, i, list_c):
    if len(list_c) == 0:
        return EOFError
    if i == len(list_c) - 1:
        return True
    else:
        if G.nodes.get(list_c[i])['height'] <= G.nodes.get(list_c[i + 1])['height']:
            return check_single(G, i + 1, list_c)
        else:
            return False


def check_right(population, G):
    for x in population:
        for y in x:
            i = 0
            if check_single(G, i, y) is False:
                return False
    return True
