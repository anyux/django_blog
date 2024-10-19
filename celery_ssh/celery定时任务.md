[TOC]

**celery链接汇总**

[celery简单使用](https://www.cnblogs.com/anyux/p/18475876)

[celery的配置文件示例](https://www.cnblogs.com/anyux/p/18476189)

[celery的定时任务](https://www.cnblogs.com/anyux/p/18478977)

### celery定时任务

```python
from datetime import timedelta
from celery.schedules import crontab

#BROKER_URL 消息代理,使用redis存储任务
BROKER_URL = "redis://127.0.0.1:6379/2"
#CELERY_RESULT_BACKEND 存储任务结果
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/3"

#设置时区
#默认使用UTC时区,如果在中国,并且同时使用定时任务
#需要设置为"Asia/Shanghai",这样时间调度会与本地时间相同
CELERY_TIMEZONE = "Asia/Shanghai"

#导入指定的任务模块
CELERY_IMPORTS = (
    'celery_app.task1',
    'celery_app.task2',
)

#定时任务配置
#CELERYBEAT_SCHEDULE是celery用于定义定时任务调度的配置字典
#包含两个定时任务,task1,task2
CELERYBEAT_SCHEDULE = {
    #定时任务名称
    'task1': {
        #任务: 'clery_app.task1.mutilpy'
        'task': 'celery_app.task1.mutilpy',
        #调度: 每隔10秒执行1次
        'schedule': timedelta(seconds=10),
        #参数: 每次执行任务时,传递的参数
        'args': (2,8)
    },
    #定时任务名称
    'task2': {
        #任务: 'celery_app.task2.task2'
        'task': 'celery_app.task2.task2',
        #调度: 每天17点33
        'schedule': crontab(hour=17,minute=33),
        #参数: 每次执行任务时,传递的参数
        'args': (4,5)
    }
}
```

启动celery worker(执行任务)
```bash
celery -A celery_app worker -l INFO
```

启动celery beat(定时任务调度器)
```bash
celery -A celery_app beat -l INFO
```

同时启动celery worker 和 celery beat
```bash
celery -A celery_app --beat -l INFO
```
beat作为定时任务调度器,只需要运行一个即可,而celery worker可以有多个

查看定时任务日志
```txt
[时间: INFO/MainProcess] Task celery_app.task1.mutilpy[task_id] 接收
[2024-10-19 10:56:45,617: INFO/MainProcess] Task celery_app.task1.mutilpy[b514f27a-359c-41a9-a9a2-35467f3484a2] received
[时间: INFO/ForkPoolWorker-2] Task celery_app.task1.mutilpy[task_id] 成功 in 执行时间: 结果
[2024-10-19 10:56:50,619: INFO/ForkPoolWorker-2] Task celery_app.task1.mutilpy[b514f27a-359c-41a9-a9a2-35467f3484a2] succeeded in 5.001623700372875s: 16
[时间: INFO/Beat] 调度: 发送任务 定时任务名称 (celery_app.task1.mutilpy)
#表示Beat开始调度任务,会被worker从消息队列中获取
[2024-10-19 10:56:55,614: INFO/Beat] Scheduler: Sending due task task1 (celery_app.task1.mutilpy)

```
