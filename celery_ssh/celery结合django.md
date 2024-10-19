[TOC]
**celery链接汇总**

[celery简单使用](https://www.cnblogs.com/anyux/p/18475876)

[celery的配置文件示例](https://www.cnblogs.com/anyux/p/18476189)

[celery的定时任务](https://www.cnblogs.com/anyux/p/18478977)

### celery与django结合

django负责web请求,celery负责异常任务调度与执行

> django 3.1版本以后支持对celery的开箱即用
> 

现在有一个django的django_blog项目如下
其中的celery.py文件用来定义celery实例
```bash
django_blog
├── settings.py
├── wsgi.py
├── urls.py
├── __init__.py
├── celery.py
└── asgi.py
```

celery.py文件
```python
import os
# 导入Celery类
from celery import Celery

#设置django项目的默认配置模块
#它向操作系统的环境变量 DJANGO_SETTINGS_MODULE 设置了默认值 django_blog.settings
#确保celery,django可以正常加载项目的配置
#os.environ是 os 模块中的一个字典,setdefault方法检查 DJANGO_SETTINGS_MODULE 环境变量
#若未设置,则设置为 django_blog.settings
#DJANGO_SETTINGS_MODULE,是Django的环境变量,用于指定django的配置文件,就是django的settings.py文件
#即celery启动时,会自动加载django_blog/settings.py文件,作为配置源
#包括数据库配置,已安装的应用,缓存设置,时区设置,语言设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_blog.settings')

#创建一个名为'django_blog'的celery实例,作为项目的celery应用对象
app = Celery('django_blog')

#使用django的配置文件配置celery
#使用'CELERY_'作为命名空间前缘的所有配置项都将会被加载
#config_from_object()是celery加载配置的方法
#django.conf:settings是django的模块路径,自动读取项目中的settings.py
#namespace='CELERY',表示celery只会加载以'CELERY_'为前缀的配置项
#以避免django和celery配置之间的冲突,确保django和celery配置分开管理
app.config_from_object('django.conf:settings', namespace='CELERY')

#自动发现并加载任务模块
#即自动发现django项目中所有应用下的tasks.py文件,并注册到 celery worker中
app.autodiscover_tasks()


#bind=True表示任务与当前任务实例绑定,任务函数会自动接收任务实例self作为第一个参数,
#以访问任务的上下文信息,通过self.request可以获取任务执行环境的详细信息,例如task_id
#ignore_result=True,表示忽略任务结果,即不将任务结果返回后端存储(redis)
@app.task(bind=True, ignore_result=True)
def debug_task(self):
#将任务执行时的上下文信息打印,包括task_id,retry_count,args,kwars,routing_key,exchange
#self.request!r 使用!r是python的repr()函数,即以开发者友好方式显示对象
    print(f'Request: {self.request!r}')
```

debug显示内容
```ini
#[时间: INFO/MainProcess] Task django_blog.celery.debug_task [task_id] 接收
[2024-10-19 14:19:15,204: INFO/MainProcess] Task django_blog.celery.debug_task[b6dc8172-94cf-43b9-b8e4-2ed9d7693c9e] received
#[时间: WARNING/ForkPoolWorker-1] 请求: 上下文信息
[2024-10-19 14:19:15,210: WARNING/ForkPoolWorker-1] Request: <Context: {'lang': 'py', 'task': 'django_blog.celery.debug_task', 'id': 'b6dc8172-94cf-43b9-b8e4-2ed9d7693c9e', 'shadow': None, 'eta': None, 'expires': None, 'group': None, 'group_index': None, 'retries': 0, 'timelimit': [None, None], 'root_id': 'b6dc8172-94cf-43b9-b8e4-2ed9d7693c9e', 'parent_id': None, 'argsrepr': '()', 'kwargsrepr': '{}', 'origin': 'gen1109832@jJkJOt1054298', 'ignore_result': True, 'replaced_task_nesting': 0, 'stamped_headers': None, 'stamps': {}, 'properties': {'correlation_id': 'b6dc8172-94cf-43b9-b8e4-2ed9d7693c9e', 'reply_to': '9c1f0c41-a440-31d6-916f-c385147c16d7', 'delivery_mode': 2, 'delivery_info': {'exchange': '', 'routing_key': 'celery'}, 'priority': 0, 'body_encoding': 'base64', 'delivery_tag': '71948a06-71fa-46f0-bf4a-bb51b3eaaba7'}, 'reply_to': '9c1f0c41-a440-31d6-916f-c385147c16d7', 'correlation_id': 'b6dc8172-94cf-43b9-b8e4-2ed9d7693c9e', 'hostname': 'celery@jJkJOt1054298', 'delivery_info': {'exchange': '', 'routing_key': 'celery', 'priority': 0, 'redelivered': False}, 'args': [], 'kwargs': {}, 'is_eager': False, 'callbacks': None, 'errbacks': None, 'chain': None, 'chord': None, 'called_directly': False, 'headers': None, '_protected': 1}>
#[时间: INFO/ForkPoolWorker-1] Task django_blog.celery.debug_task [task_id] 成功 in 花费时间: 返回结果    
[2024-10-19 14:19:15,211: INFO/ForkPoolWorker-1] Task django_blog.celery.debug_task[b6dc8172-94cf-43b9-b8e4-2ed9d7693c9e] succeeded in 0.0010590003803372383s: None
```

django_blog/__init__.py
```python
#django启动后,celery应用可以正常运行,且可以捕获任务到worker中
#app表示从celery.py文件中创建的celery实例
#as celery_app为重命名实例
from .celery import app as celery_app

#__all__为特殊变量,表明当你从__init__.py中导入时,celery_app是唯一的暴露变量
#它限制了外部模块在使用`from . import *`语句时仅能导入`celery_app`,避免不必要的内容导入
__all__ = ('celery_app',)
```

> 在__init__.py文件中导入,可以确保'shared_task'装饰器正常工作,通过导入Celery实例,可以确实在django启动时已经加载好了,所有的shared_task都可以正常使用它
> django项目启动时自动导入celery应用,这确保了celery与django集成是正常的 
> 

settings.py文件中celery的配置项
```python
# Celery 配置项
#追踪任务的启动状态,为True时,任务状态更新为STARTED,而不是直接从PENDING,跳到SUCCESS,FAILURE
#当worker任务执行时,状态变为STARTED,任务完成后更新为SUCCESS或FAILURE,可以看到任务是否执行
#对于flower等监控工具,追踪任务状态
#状态转换过程
#PENDING: 任务已创建,未被worker执行
#STARTED: 任务被worker接收,正在执行
#SUCCESS: 任务执行成功
#FAILURE: 任务执行失败
CELERY_TASK_TRACK_STARTED = True
#设置硬超时时间
#指任务最大运行时间,30 * 60 表示设置30分钟超时时间
#超过硬超时时间就被强制结束任务
#作用是防止任务卡死,资源控制,及长时间的任务
CELERY_TASK_TIME_LIMIT = 30 * 60
#设置软超时时间为25分钟
#软超时时间会发现超时信号,让任务自己决定如何处理
CELERY_SOFT_TIME_LIMIT = 25 * 60

CELERY_TIMEZONE="Asia/Shanghai"
CELERY_BROKER_URL = 'redis://192.168.255.181:6379/0'
CELERY_RESULT_BACKEND  = 'redis://192.168.255.181:6379/1'
#确保任务结果会被存储
#为True,任务结果丢弃
#为False,任务结果存储在CELERY_RESULT_BACKEND中
#要获取结果值时,设置为False,如数据处理任务,文件上传完成后通知用户,或者任务返回处理结果
#消息通知,邮件发送,推送消息,可以通过任务结果查询确保任务成功完成
#不需要关注任务结果时,例如清理任务,同步任务
CELERY_TASK_IGNORE_RESULT = False
```

celery应用将自动发现所有django应用下的tasks.py
```bash
#创建项目
python manage.py start app1
cd app1
touch tasks.py
```
文件结构示例
```bash

```

















