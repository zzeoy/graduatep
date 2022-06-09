import random
from System.tool.DataProcess import trans_Json, process_res, process_dag, height_num
from System.tool.Tools import cal, check_right, check_single
from System.tool.Unit import Pc, P_inc, Pm, T, Num, context
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput


# 在DAG图中添加height属性
def add_height(G):
    Height = 0
    for i in G.nodes:
        temp = height_num(G, i)
        if temp > Height:
            Height = temp
        G.nodes.get(i)['height'] = temp
    return G, Height


def exchange_function(list1, list2, G, h):
    pos1 = len(list(G.nodes)) + 1
    pos2 = len(list(G.nodes)) + 1
    for x in range(len(list1)):
        if G.nodes.get(list1[x])['height'] >= h:
            pos1 = x
            break
    for x in range(len(list2)):
        if G.nodes.get(list2[x])['height'] >= h:
            pos2 = x
            break
    if pos1 != len(list(G.nodes)) + 1 and pos2 != len(list(G.nodes)) + 1:
        temp = list1[pos1:]
        temp2 = list2[pos2:]
        del list1[pos1:]
        list1 = list1 + temp2
        del list2[pos2:]
        list2 = list2 + temp
    elif pos1 == len(list(G.nodes)) + 1 and pos2 != len(list(G.nodes)) + 1:
        temp = list2[pos2:]
        list1 = list1 + temp
        del list2[pos2:]
    elif pos1 != len(list(G.nodes)) + 1 and pos2 == len(list(G.nodes)) + 1:
        temp = list1[pos1:]
        list2 = list2 + temp
        del list1[pos1:]
    return list1, list2


# 两个个体进行交叉
def two_cross_function(G, list1, list2, M, Height):
    h = random.randint(0, Height)
    for i in range(M):
        list1[i], list2[i] = exchange_function(list1[i], list2[i], G, h)
    return list1, list2


# 交叉
def cross_function(population, G, fitness, M, Height):
    # 随机在其他的个体中选择两个
    # 选择适应度高的进行交叉
    for subpopulation in population:
        p = random.random()
        pos = population.index(subpopulation)
        # 锦标赛选择
        if p <= Pc:
            choice1, choice2 = random.sample(range(len(population)), 2)
            while choice1 == pos or choice2 == pos:
                choice1, choice2 = random.sample(range(len(population)), 2)
            if fitness[choice1] > fitness[choice2]:
                two_cross_function(G, subpopulation, population[choice1], M, Height)
            else:
                two_cross_function(G, subpopulation, population[choice2], M, Height)
        test = 0
        for i in range(len(subpopulation)):
            test = test + len(subpopulation[i])
        if test > len(list(G.nodes)):
            print("交叉出错", population.index(subpopulation))
        for y in subpopulation:
            if check_single(G, 0, y) is False:
                print("交叉出错", population.index(subpopulation))
    return population


# 内部杂交
def inter_cross_function(population, G, M, Height):
    # 随机该个体中的两个染色体
    for subpopulation in population:
        p = random.random()
        if p <= P_inc:
            h = random.randint(0, Height)
            choice1, choice2 = random.sample(range(M), 2)
            subpopulation[choice1], subpopulation[choice2] = exchange_function(subpopulation[choice1],
                                                                               subpopulation[choice2], G, h)
            test = 0
            for i in range(len(subpopulation)):
                test = test + len(subpopulation[i])
            if test > len(list(G.nodes)):
                print("内部交叉出错", population.index(subpopulation))
            for y in subpopulation:
                if check_single(G, 0, y) is False:
                    print("内部交叉出错", population.index(subpopulation))
    return population


# 选择
def selection(population, fitness):
    select = []
    # 下一代进行轮盘选择
    p = []
    lp = []
    cm_p = []
    for i in range(len(population)):
        p.append(fitness[i] / sum(fitness))
        lp.append(0)
        cm_p.append(random.random())
    # 计算累计概率的计算
    for temp in range(len(p)):
        for j in range(temp):
            lp[temp] = lp[temp] + p[j]
    cm_p.sort()
    for k in range(len(population)):
        # 通过随机数来决定是否进入下一代
        if lp[k] >= cm_p[k]:
            select.append(population[k])
    if len(select) < 10:
        print("选择不足10个", len(select))
        return population
    else:
        print("选择后的个体数量为：", len(select))
        return select


# 找到该高度的位置
def find_height_pos(h, list1, G):
    for i in range(len(list1)):
        h2 = G.nodes.get(list1[i])['height']
        if h2 >= h:
            return i
    return len(list1)


# 变异
def mutable(population, G, Height):
    for subpopulation in population:
        p = random.random()
        if p <= Pm:
            # 用于debug的代码
            # for y in subpopulation:
            #     if check_single(G, 0, y) is False:
            #         print("变异前出错", population.index(subpopulation))
            #     else:
            #         print("变异前正常", y)
            length = []
            # 先定位到相同高度
            h = random.randint(0, Height)
            pos = []
            for x in subpopulation:
                need = True
                for y in range(len(x)):
                    if G.nodes.get(x[y])['height'] >= h:
                        length.append(len(x[y:]))
                        pos.append(y)
                        need = False
                        break
                if need:
                    length.append(0)
                    pos.append(len(x))
            # 寻找之后任务最多的和任务最少的，随机进行任务迁移
            max1 = max(length)
            min1 = min(length)
            if max != min:
                choice1 = length.index(max1)
                choice2 = length.index(min1)
                po1 = pos[choice1]
                num = random.randint(po1, len(subpopulation[choice1]) - 1)
                temp = subpopulation[choice1][num]
                h_po = find_height_pos(G.nodes.get(temp)['height'], subpopulation[choice2], G)
                subpopulation[choice1].pop(num)
                subpopulation[choice2].insert(h_po, temp)
            test = 0
            for i in range(len(subpopulation)):
                test = test + len(subpopulation[i])
            if test > len(list(G.nodes)):
                print("变异出错", population.index(subpopulation))
            for y in subpopulation:
                if check_single(G, 0, y) is False:
                    print("变异出错", population.index(subpopulation))
    return population


# 适应函数的计算：
def fitness_cal(population, G, M):
    fitness = []
    C = calculate_m(G)
    for subpopulation in population:
        fitness.append(C - max(cal(subpopulation, G, M)))
    return fitness


# 得到下一代种群
def get_nest(population, G, M, Height):
    # 适应函数的计算
    fitness = fitness_cal(population, G, M)
    if fitness.count(0) == len(fitness):  # 如果全部为0，则不进行交叉和变异
        generation = [population[0]]
        return generation
    # 个体交叉
    next_generation = cross_function(population, G, fitness, M, Height)
    x1 = check_right(next_generation, G)
    while x1 is False:
        print("交叉后的个体不合法，重新交叉")
        next_generation = cross_function(population, G, fitness, M, Height)
    print("交叉后的个体数量为：", len(next_generation))
    # 内部杂交
    next_generation_2 = inter_cross_function(next_generation, G, M, Height)
    x2 = check_right(next_generation_2, G)
    while x2 is False:
        print("内部杂交后的个体不合法，重新内部杂交")
        next_generation_2 = inter_cross_function(next_generation, G, M, Height)
    print("内部杂交后的个体数量为：", len(next_generation_2))
    # 变异
    next_generation_3 = mutable(next_generation_2, G, Height)
    x3 = check_right(next_generation_3, G)
    while x3 is False:
        print("变异后的个体不合法，重新变异")
        next_generation_3 = mutable(next_generation_2, G, Height)
    print("变异后的个体数量为：", len(next_generation_3))
    fitness_3 = fitness_cal(next_generation_3, G, M)
    # 轮盘赌注选择
    next_generation_4 = selection(next_generation_3, fitness_3)
    print(len(next_generation_4))
    return next_generation_4


# 该函数为了这一高度的基因随分配到处理机上
def random_machine(range1, num):
    list1 = []
    if range1 == 0:
        for i in range(num):
            list1.append(0)
        return list1
    if num <= range1 + 1:
        while len(list1) < num:
            temp = random.randint(0, range1)
            if temp not in list1:
                list1.append(temp)
    else:
        div = num // (range1 + 1)
        mod = num % (range1 + 1)
        for i in range(div):
            while len(list1) < ( range1 + 1)*(i+1):
                temp = random.randint(0, range1)
                if list1.count(temp) <= i:
                    list1.append(temp)
        if mod == 0:
            pass
        else:
            while len(list1) < num:
                temp = random.randint(0, range1)
                if list1.count(temp) <= div :
                    list1.append(temp)
    return list1


# 初史种群
def get_initial(H, M):
    population = []
    # 每次population中产生num个个体
    for i in range(Num):
        subpopulation = []
        for t in range(M):
            pop = []
            subpopulation.append(pop)
        for x in range(len(H)):
            list1 = random_machine(M - 1, len(H[x]))  # 随机出任务被分配出得M
            for y in range(len(list1)):
                subpopulation[list1[y]].append(H[x][y])
        population.append(subpopulation)
    return population


def calculate_m(G):
    value = 0
    for x in G.nodes:
        value += G.nodes.get(x)['weight']
    return value


# 找出方案
def find_stage(population, G, M):
    # 找出最优解
    best = population[0]
    time = calculate_m(G)
    for subpopulation in population:
        temp = max(cal(subpopulation, G, M))
        if temp < time:
            time = temp
            best = subpopulation
        # 为了更新start_time和end_time
        time = max(cal(best, G, M))
    return best, time


# 遗传算法
def GA(G, M):
    H = process_dag(G)
    G, Height = add_height(G)
    population = get_initial(H, M)
    if M <= 1:
        time = max(cal(population[0], G, M))
        best = process_res(G, population[0])
        return best, time
    for i in range(T):
        population = get_nest(population, G, M, Height)
        print('population:', len(population))
        if len(population) <= Num / 10:
            break
    best, time = find_stage(population, G, M)
    best = process_res(G, best)
    return best, time

# graphviz = GraphvizOutput() # 语句1
#     # 语句2：在当前目录生成名为 basic.png 的调用关系图
# graphviz.output_file = 'basic.png'
# with PyCallGraph(output=graphviz):
#     G = trans_Json(context)
#     GA(G,3)
