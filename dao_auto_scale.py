#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@version: 1.0.0
@author: zheng guang
@contact: zg.zhu@daocloud.io
@time: 16/3/28 下午9:05
"""
import requests, json, time,os
from logger import logger

api_url = 'https://api.daocloud.io'


class Daocloud():
    def __init__(self, token):
        self.__token__ = token
        self.__auth__ = 'token'

    def __init__(self, username, password):
        self.__username__ = username
        self.__password__ = password
        self.__auth__ = 'password'

    def token(self, username, password):
        json_data = {'email_or_mobile': username, 'password': password}
        headers = {'Content-Type': 'application/json'}
        token_json = requests.post(api_url + "/access-token", data=json.dumps(json_data), headers=headers).json()
        #logger.info('get token: %s', token_json)
        return token_json['access_token']

    def __token__(self):
        if (self.__auth__ == 'password'):
            return self.token(self.__username__, self.__password__)
        return self.__token__

    def app(self, app_name, space=''):
        headers = {'Authorization': self.__token__()}
        if space and len(space) >= 1:
            headers['UserNameSpace'] = space
        app_json = requests.get(api_url + '/v1/apps', headers=headers).json();
        #logger.info('apps json: %s', app_json)
        for app in app_json['apps']:
            if app['name'] == app_name:
                #logger.info('app json: %s', app)
                app_detaild_json = requests.get(api_url + '/v1/apps/' + app['app_id'] + '/details',
                                                headers=headers).json();
                return app_detaild_json

        logger.error("can not find app_name: %s ,space:%s", app_name, space)
        raise Exception('can not find app' + app_name)

    def metric_cpu(self, app_id, space=''):
        headers = {'Authorization': self.__token__()}
        if space and len(space) >= 1:
            headers['UserNameSpace'] = space

        metric_cpu = requests.get(api_url + '/v1/apps/' + app_id + '/metrics-cpu?period=hour', headers=headers).json();
        #logger.info('metric_cpu json: %s', metric_cpu)
        return metric_cpu
    #升级一倍
    def app_update_instance_type(self, app_id,instance_type, space=''):
        headers = {'Authorization': self.__token__()}
        if space and len(space) >= 1:
            headers['UserNameSpace'] = space

        result = requests.patch(api_url + '/v1/apps/' + app_id ,data=json.dumps({"metadata":{"instance_type":instance_type}}), headers=headers).json();

        logger.info('app_update_instance_type result json: %s', result)
        return result
    def metric_mem(self, app_id, space=''):
        headers = {'Authorization': self.__token__()}
        if space and len(space) >= 1:
            headers['UserNameSpace'] = space

        metric_mem = requests.get(api_url + '/v1/apps/' + app_id + '/metrics-mem?period=hour', headers=headers).json();
        #logger.info('metric_mem json: %s', metric_mem)
        return metric_mem

    def scale(self, app_id, instances=1, space=''):
        headers = {'Authorization': self.__token__(), 'Content-Type': 'application/json'}
        if space and len(space) >= 1:
            headers['UserNameSpace'] = space

        metric_mem = requests.post(api_url + '/v1/apps/' + app_id + '/actions/scale',
                                   data=json.dumps({'instances': instances}), headers=headers).json();
        #logger.info('scale result json: %s', metric_mem)
        return metric_mem


"""
cpu  cpu百分比.默认:-1,不检测;
mem  mem百分比.默认:-1,不检测;
scale_num_each 每次扩展的个数.默认1
scale_instance_type 是否先升级配置,默认2,默认会扩展两倍
TODO 暂不支持 SR
"""


def auto_scaling(username, password, app_name, cpu=-1, memory=-1, scale_num_each=1,scale_instance_type=2, space=''):
    scale_instance_type=int(scale_instance_type)

    daocloud = Daocloud(username, password)

    app = daocloud.app(app_name, space)
    need_scale = False
    if (cpu > -1):
        current_cpu = 0
        metric_cpu = daocloud.metric_cpu(app['app_id'], space)

        if (metric_cpu['cpu_usage'] and len(metric_cpu['cpu_usage']) > 1):
            current_cpu = float(metric_cpu['cpu_usage'][-1][1]) * 100
        logger.debug('current_cpu :%s', current_cpu)
        if (current_cpu*100 > cpu):
            need_scale = True
    if (memory > -1):
        current_memory = 0
        total_memory = int(app['cf_app_summary']['memory'])
        metric_mem = daocloud.metric_mem(app['app_id'], space)
        if (metric_mem['memory_usage'] and len(metric_mem['memory_usage']) > 1):
            current_memory = float(metric_mem['memory_usage'][-1][1]) / 1024.0 / 1024.0
        logger.debug('total memory: %s   current_memory :%s     use:%s%%', total_memory, current_memory,
                    current_memory / total_memory * 100)
        if (current_memory / total_memory * 100 > memory):
            need_scale = True
    if need_scale:
        current_instance_type_int=int(app['instance_type'][0:-1])
        if(scale_instance_type >1 and current_instance_type_int<16):
            logger.info('update app[%s] instance_type to:%s', app_name, str(current_instance_type_int*scale_instance_type)+'x')
            daocloud.app_update_instance_type(app['app_id'],str(current_instance_type_int*scale_instance_type)+'x',space)

        else:
            logger.info('app[%s] scalea to:%s', app_name, int(app['cf_app_summary']['instances']) + scale_num_each)
            daocloud.scale(app['app_id'], int(app['cf_app_summary']['instances']) + scale_num_each)

        app_status='init'
        while app_status != 'STAGED':
            logger.info('wait to scale finish: app status :%s',app_status)
            time.sleep(2)# 等待scale finish
            app = daocloud.app(app_name, space)
            app_status=app['cf_app_summary']['package_state']
        logger.info('app[%s] scalea to:%s [instance_type:%s] finish', app_name, app['cf_app_summary']['instances'],app['instance_type'])

if __name__ == '__main__':

    while True:
        auto_scaling(os.getenv('daocloud_username'), os.getenv('daocloud_password'), os.getenv('daocloud_appname'), os.getenv('daocloud_cpu_max','80'), os.getenv('daocloud_memory_max','40'), os.getenv('daocloud_scale_num_each','1'),os.getenv('daocloud_sinstance_type_num',2), space=os.getenv('daocloud_space',''))
        time.sleep(1)
