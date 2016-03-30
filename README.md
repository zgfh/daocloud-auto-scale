# dao-auto-scale


#构建
docker build .


# config

daocloud_username
daocloud_password

daocloud_appname 自动scale的appname
daocloud_space daocloud组织名,默认为'',表示个人

daocloud_cpu_max :cpu  cpu百分比.默认:80,不检测;
daocloud_memory_max :mem百分比.默认:40,不检测;
daocloud_scale_num_each :每次扩展的个数.默认1
daocloud_instance_type_num :每次升级配置的倍数,设置为1表示不升级配置,默认为2


