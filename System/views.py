import json
import os
from pathlib import Path
import random
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from System.tool.CreateData import create
from System.tool.DataProcess import trans_Json, is_json, trans_to_tree
from System.algorithm import GA, TA
from System.models import Record, Res, Taskset


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
    recommend = '遗传调度算法'
    str_re = str(content)
    str_re = str_re.replace("\'", "\"")
    str_re = str_re.replace(" ", "")
    str_re = str_re.replace("\r\n", "")
    if len(list(G.nodes)) <= 10:
        recommend = '传统调度算法'
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
        task = json.loads(content)
        if len(task['Task']) > 10:
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
    for i in range(10):
        context = create()
        context= context.replace("\'", "\"")
        context = context.replace("None", "null")
        task = Taskset(name='dataset' + str(i+1), context=context, machine=str(random.randint(1, 30)), train_times=0,
                       recommend='test数据')
        task.save()
    return HttpResponse("创建成功")


def delete_all(request):
    Taskset.objects.all().delete()
    return HttpResponse("删除成功")
