[TOC]


celery的配置文件示例

[celer简单示例](https://www.cnblogs.com/anyux/p/18475876)


```bash
tree  -I 'containerd|vminit|__pycache__'
.
# app.py属于生产者
├── app.py
# celery_app用于配置消费者及队列信息
└── celery_app
# confi.py配置信息
    ├── config.py
# __init__.py celery实例初始化文件
    ├── __init__.py
# task1,task2用于注册函数
    ├── task1.py
    └── task2.py
```

#### 生产者
app.py 


```python
from celery_app import task1,task2

#调用delay()方法,任务被异步提交给消息队列,celery worker后台取出任务并执行
#返回AsyncResult对象,可以根据这个对象跟踪任务状态,结果
#任务的异步执行流程,1.调用delay()提交任务到消息队列,2.返回AsyncResult,查询结果
t2=task2.task2.delay(3,4)
print(t2)

t1 = task1.mutilpy.delay(2,10)
print(t1)

```

#### 消费者配置信息
celery_app/config.py
```python
#BROKER_URL 是消息代理(broker)的地址
BROKER_URL = "redis://127.0.0.1:6379/2"
#CELERY_RESULT_BACKEND是任务的结果后端
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/3"
#CELERY_TIMEZONE 设置时区,定时任务,会用到
CELERY_TIMEZONE = "Asia/Shanghai"
#UTC

#Celery 可以在启动时自动加载和注册任务模块
CELERY_IMPORTS = (
    'celery_app.task1',
    'celery_app.task2',
)

```

celery_app/__init__.py
```python
from celery import Celery

#创建celery应用实例,名称为demo,用于区分不同的celery实例
#这个实例是celery的核心对象,负责任务调度,任务路由,配置加载
app = Celery('demo')

#通过 Celery 实例加载配置
app.config_from_object('celery_app.config')
```

celery_app/task1.py
```python
#导入Celery的app实例
from celery_app import app
import time

#app.task将普通函数转换为Celery任务,这个任务可以通过Celery的异步机制调度执行
@app.task
def mutilpy(x,y):
    time.sleep(5)
    return x * y 
```

celery_app/task2.py
```python
from celery_app import app
import time

@app.task
def task2(x,y):
    time.sleep(20)
    return x / y
```

celery worker启动
```bash
celery -A celery_app worker -l INFO
```

查看celery启动日志
```ini
[config]
# app: demo表示运行的celery实例名称为demo
.> app:         demo:0x7f0014e6f3d0
# transport 表示消息代理(broker),它负责从生产者到消费者的传递
.> transport:   redis://127.0.0.1:6379/2
# results 表示结果后端,用于存储任务执行的结果
.> results:     redis://127.0.0.1:6379/3
# concurrency 表示celery worker可以同时处理两个任务
.> concurrency: 2 (prefork)
# 表示可以通过-E,--events启用事件监控
.> task events: OFF (enable -E to monitor tasks in this worker)

#表示celery worker 当前监听的队列
[queues]
# celery表示队列名字,默认Celery使用名为celery的队列接收和处理任务
#exchange是消息交换机,类型是direct,direct交换机表示消息将直接路由到具有匹配路由键的队列中
#key=celery是路由键,表示只有带有路由键的celery会被路由到这个队列,默认所有任务都会通过这个路由键发送到celery队列
.> celery           exchange=celery(direct) key=celery

#表示celery worker启动时,已经加载和注册的所有任务
[tasks]
#表示2个已经加载的任务
. celery_app.task1.mutilpy
. celery_app.task2.task2

```

调动生产者
```python
python app.py 
#返回task_id
#49c5e568-7fb2-49ab-8be7-c5ee6124011f
#71b170fc-09a9-476e-be91-567dd78b163c
```
返回结果
```txt
#日志格式
#[时间: INFO/MainProcess] Task celery_app.tasks1.mutilpy[task_id] received
#任务接收
[2024-10-19 09:06:35,842: INFO/MainProcess] Task celery_app.task1.mutilpy[414dc010-f7f7-473d-83dc-282d4dfc4cca] received
#任务成功
#每个任务由不同的celery worker进程(ForkPoolWorker)执行.
#[时间: INFO/ForkPoolWorker-2] Task celery_app.task1.mutilpy[task_id] 状态 in 花费时间: 结果
[2024-10-19 09:06:40,844: INFO/ForkPoolWorker-2] Task celery_app.task1.mutilpy[414dc010-f7f7-473d-83dc-282d4dfc4cca] succeeded in 5.0014993995428085s: 20
```