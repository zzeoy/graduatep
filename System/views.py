import json
import os
from pathlib import Path
import random
import pandas
from sklearn.naive_bayes import GaussianNB  # 高斯朴素贝叶斯函数
import pickle
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
from pandas.core.frame import DataFrame
from System.tool.CreateData import create
from System.tool.DataProcess import trans_Json, is_json, trans_to_tree
from System.algorithm import GA, TA
from System.models import Record, Res, Taskset
import csv


def index(request):
    return render(request, 'index.html', {})


# 关于遗传算法的介绍 和使用数据
def about(request):
    return render(request, 'about.html', {})


# 在线训练
def online(request):
    context = None
    return render(request, 'online.html', context)


def online_train(request):
    content = request.POST.get("data", None)
    machine = request.POST.get("machine", None)
    if is_json(content) is False:
        return HttpResponse("没有上传内容或格式不正确")
    content.replace("null", "None")
    prepared_data = content
    G = trans_Json(content)
    content = trans_to_tree(G)
    str_re = str(content)
    str_re = str_re.replace("\'", "\"")
    str_re = str_re.replace(" ", "")
    str_re = str_re.replace("\r\n", "")
    data = [[int(machine), G.number_of_nodes(), G.number_of_edges()]]
    data = DataFrame(data)
    with open('model.pkl', 'rb') as f:
        clf = pickle.load(f)
    recommend = clf.predict(data)
    if recommend == 'TA':
        recommend = '传统调度算法'
    else:
        recommend = '遗传调度算法'
    context = {
        'content': str_re,
        'recommend': recommend,
        'machine': machine,
        'prepare': prepared_data,
    }
    request.session['prepare_data'] = prepared_data
    request.session['machine'] = machine
    request.session['content'] = str_re
    return render(request, 'online.html', context)


def online_GA_train(request):
    context = request.session.get("prepare_data")
    machine = request.session.get("machine")
    content = request.session.get("content")
    G = trans_Json(context)
    M = int(machine)
    sample, time = GA.GA(G, M)
    str_re = str({"schedule": str(sample), "result": time})
    str_re = str_re.replace("\'", "\"")
    str_re = str_re.replace("\r\n", "")
    return render(request, 'online.html', {'result': str_re, 'content': content})


def online_TA_train(request):
    context = request.session.get("prepare_data")
    machine = request.session.get("machine")
    content = request.session.get("content")
    G = trans_Json(context)
    M = int(machine)
    sample, time = TA.TA(G, M)
    str_re = str({"schedule": str(sample), "result": time})
    str_re = str_re.replace("\'", "\"")
    str_re = str_re.replace("\r\n", "")
    return render(request, 'online.html', {'result': str_re, 'content': content})


# 上传方法
def upload(request):
    BASE_DIR = Path(__file__).resolve().parent.parent
    if request.method == 'GET':
        return render(request, 'about.html')
    elif request.method == 'POST':
        content = request.FILES.get("upload", None)
        name = request.POST.get("name", None)
        machine = request.POST.get("machine", None)
        if not content:
            return HttpResponse("没有上传内容")
        SAVE_DIR = os.path.join(BASE_DIR, "uploadFile")
        position = os.path.join(SAVE_DIR, content.name)
        # 获取上传文件的文件名，并将其存储到指定位置
        storage = open(position, 'wb+')  # 打开存储文件
        for chunk in content.chunks():  # 分块写入文件
            storage.write(chunk)
        storage.close()  # 写入完成后关闭文件
        f = open(position, 'r')
        content = f.read()
        content.replace("null", "None")
        if is_json(content) is False:
            f.close()
            os.remove(position)
            return HttpResponse("内容格式不正确")
        G = trans_Json(content)
        with open('model.pkl', 'rb') as f:
            model = pickle.load(f)
        data = [[int(machine), G.number_of_nodes(), G.number_of_edges()]]
        data = DataFrame(data)
        result = model.predict(data)
        if result[0] == "GA":
            recommend = '遗传调度算法'
        else:
            recommend = '传统调度算法'
        t = Taskset(machine=machine, name=name, context=content, train_times=0, recommend=recommend)
        # 上传的数据存到数据库中
        t.save()
        f.close()
        os.remove(position)
        return HttpResponse("上传成功")  # 返回客户端信息
    else:
        return HttpResponseRedirect("不支持的请求方法")


# 提取数据库中上传的数据显示在页面上以进行操作
def statistics(request):
    taskset = Taskset.objects.all()
    dataset = []
    machine = []
    for task in list(taskset):
        temp = [task.name, task.uploadDate, task.recommend, task.train_times]
        temp2 = {
            'showdata': temp,
            'machine': task.machine,
            'task_id': task.id
        }
        dataset.append(temp2)

    context = {
        'dataset': dataset,
    }
    return render(request, 'statistics.html', context)


def data_show(request, task_id):
    task = Taskset.objects.get(id=task_id)
    context = str(task.context)
    name = str(task.name)
    G = trans_Json(context)
    content = trans_to_tree(G)
    str_re = str(content)
    str_re = str_re.replace("\'", "\"")
    str_re = str_re.replace(" ", "")
    str_re = str_re.replace("\r\n", "")
    return render(request, 'data.html', {'content': str_re, 'name': name})


# 训练的历史记录来显示训练结果
def history(request):
    recordset = Record.objects.all()
    dataset = []
    if Record.objects.all().count() != 0:
        for record in list(recordset):
            temp = [record.train_data, record.train_time, record.train_type]
            temp2 = {
                "showdata": temp,
                "record_id": record.id
            }
            dataset.append(temp2)
    context = {
        'dataset': dataset,
    }
    return render(request, 'history.html', context)


# 使用GA算法来分配任务
def GA_algorthm(request, task_id, machine):
    # 将数据库中的数据提取出来进行包装
    # 简单的训练数据
    graphviz = GraphvizOutput()  # 语句1
    # 语句2：在当前目录生成名为 basic.png 的调用关系图
    graphviz.output_file = 'basic.png'
    with PyCallGraph(output=graphviz):
        task_set = Taskset.objects.get(id=task_id)
        context = task_set.context
        task_set.machine = machine
        G = trans_Json(context)
        # 加工成DAG图
        M = machine
        sample, time = GA.GA(G, M)
        task_set.train_times = task_set.train_times + 1
        task_set.save()
        r1 = Record(train_data=task_set.name, task_id=task_id, train_type='GA')
        r1.save()
        r2 = Res(schedule=str(sample), result=time, history_id=r1.id)
        r2.save()
        return HttpResponse("训练结束,请返回历史记录查看结果")


# 使用GA算法来分配任务
def TA_algorthm(request, task_id, machine):
    # 将数据库中的数据提取出来进行包装
    # 简单的训练数据
    task_set = Taskset.objects.get(id=task_id)
    context = task_set.context
    G = trans_Json(context)
    task_set.machine = machine
    M = machine
    graphviz = GraphvizOutput()  # 语句1
    # 语句2：在当前目录生成名为 basic.png 的调用关系图
    graphviz.output_file = 'basic2.png'
    with PyCallGraph(output=graphviz):
        # 加工成DAG图
        sample, time = TA.TA(G, M)
        task_set.train_times = task_set.train_times + 1
        task_set.save()
        r1 = Record(train_data=task_set.name, task_id=task_id, train_type='TA')
        r1.save()
        r2 = Res(schedule=str(sample), result=time, history_id=r1.id)
        r2.save()
        return HttpResponse("训练结束,请返回历史记录查看结果")


def delete_task(request, task_id):
    # 将数据库中的数据提取出来删除
    task_set = Taskset.objects.get(id=task_id)
    task_set.delete()
    return HttpResponse("删除成功")


def delete_record(request, record_id):
    # 将数据库中的数据提取出来删除
    record = Record.objects.get(id=record_id)
    record.delete()

    resset = Res.objects.filter(history_id=record.id)
    for res in list(resset):
        res.delete()
    return HttpResponse("删除成功")


# 显示训练结果
def Result(request, record_id):
    result = Res.objects.get(history_id=record_id)
    record = Record.objects.get(id=record_id)
    task = Taskset.objects.filter(id=record.task_id)
    if len(list(task)) == 0:
        empty_data = "True"
    else:
        empty_data = None
    str_re = str(result)
    str_re = str_re.replace("\'", "\"")
    return render(request, 'result.html', {'result': str_re, 'empty_data': empty_data})


def create_task(request):
    context = create()
    context = context.replace("\'", "\"")
    context = context.replace("None", "null")
    task = Taskset(name='random_dataset', context=context, machine=str(random.randint(1, 5)),
                   train_times=0,
                   recommend='test数据')
    task.save()
    return HttpResponse("创建成功")


def train_model(request):
    data = pandas.read_csv('data1.csv')
    x_train = data.iloc[:, [0, 1, 2]].values
    y_train = data.iloc[:, 3].values
    print(x_train)
    print(y_train)
    BYS = GaussianNB().fit(x_train, y_train)

    test_data = pandas.read_csv('data2.csv')
    compare = test_data.iloc[:, 3].values
    test = test_data.iloc[:, [0, 1, 2]].values
    answer_BYS = BYS.predict(test)
    num = 0
    for i in range(len(compare)):
        if compare[i] == answer_BYS[i]:
            num = num + 1
    x = num / len(compare)
    print("该模型的预测准确度为：",x)
    pickle.dump(BYS, open('model.pkl', 'wb'))
    return HttpResponse("训练保存成功")


def create_task_test(request):
    for i in range(1000):
        context = create()
        context = context.replace("\'", "\"")
        context = context.replace("None", "null")
        task = Taskset(name='dataset' + str(i + 4001), context=context, machine=str(random.randint(1, 5)),
                       train_times=0,
                       recommend='test数据')
        task.save()
    taskset = Taskset.objects.all()

    for task in taskset:
        M = task.machine
        G = trans_Json(task.context)
        sample1, time1 = TA.TA(G, M)
        sample2, time2 = GA.GA(G, M)
        print('TA', time1, 'GA', time2)
        if time1 <= time2:
            task.recommend = "TA"
        else:
            task.recommend = "GA"
        task.save()
    return HttpResponse("保存成功")


def export_data(request):
    f = open('data1.csv', 'w', encoding='utf-8', newline="")
    f2 = open('data2.csv', 'w', encoding='utf-8', newline="")
    csv_writer = csv.writer(f)
    csv_writer.writerow(['machine', 'task_num', 'link_num', 'recommend'])
    csv_writer2 = csv.writer(f2)
    csv_writer2.writerow(['machine', 'task_num', 'link_num', 'recommend'])
    count1 = 0
    count2 = 0
    taskset = Taskset.objects.all()
    for task in taskset:
        context = task.context
        G = trans_Json(context)
        if count1 <= 600:
            if task.recommend == 'GA':
                count1 = count1 + 1
                csv_writer.writerow([task.machine, G.number_of_nodes(), G.number_of_edges(), task.recommend])
        elif count1 > 600 and count1 <= 800:
            if task.recommend == 'GA':
                count1 = count1 + 1
                csv_writer2.writerow([task.machine, G.number_of_nodes(), G.number_of_edges(), task.recommend])
        if count2 <= 600:
            if task.recommend == 'TA':
                count2 = count2 + 1
                csv_writer.writerow([task.machine, G.number_of_nodes(), G.number_of_edges(), task.recommend])
        elif count2 > 600 and count2 <= 800:
            if task.recommend == 'TA':
                count2 = count2 + 1
                csv_writer2.writerow([task.machine, G.number_of_nodes(), G.number_of_edges(), task.recommend])
    return HttpResponse("文件提取成功")


def delete_all(request):
    Taskset.objects.all().delete()
    return HttpResponse("删除成功")


def search_GA(request):
    taskset2 = Taskset.objects.filter(recommend='TA')
    taskset = Taskset.objects.filter(recommend='GA')
    print("任务的数量", taskset.count() + taskset2.count())
    print("其中推荐遗传算法有", taskset.count())
    print("其中推荐传统算法有", taskset2.count())
    return HttpResponse("搜索成功")
