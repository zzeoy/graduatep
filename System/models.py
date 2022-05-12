# Create your models here.
from django.db import models
from django.contrib.auth.models import User


# 任务集
class Taskset(models.Model):
    name = models.CharField(max_length=100)
    machine = models.IntegerField('处理机数量')
    context = models.TextField('任务内容')
    uploadDate = models.DateTimeField('上传的时间', auto_now=True)
    train_times = models.IntegerField('训练次数')
    recommend = models.CharField('推荐调度算法',max_length=100)

    def __str__(self):
        result = {"recommend":self.recommend,"name": self.name, "machine": self.machine, "time": str(self.uploadDate), "训练次数": self.train_times}
        return str(result)


# 训练结果
class Res(models.Model):
    schedule = models.TextField('调度分配')
    result = models.IntegerField('所需时间')
    history_id = models.IntegerField('对应历史记录')

    def __str__(self):
        result = {"schedule": self.schedule, "result": str(self.result)}
        return str(result)


# 训练记录
class Record(models.Model):
    train_time = models.DateTimeField('训练时间', auto_now=True)
    task_id = models.IntegerField("对应的任务训练")
    train_type = models.TextField('训练方式')
    train_data = models.CharField('训练数据名称', max_length=100)
    type = models.CharField('训练方式', max_length=100)

    def __str__(self):
        result = {"data_name": self.train_data, "train_time": str(self.train_time), "task_id": str(self.task_id),
                  "type": self.type}
        return str(result)
