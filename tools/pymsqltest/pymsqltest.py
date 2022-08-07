""" 引入PyMySQL模块
    创建连接对象
    使用连接对象创建游标对象
    准备需要使用的sql语句
    使用游标对象执行sql语句(如果是数据修改的操作, 会返回受影响的行数)
    如果执行语句是查询操作, 需要使用游标对象获取查询结果
    关闭游标对象
    关闭连接对象"""
#参考http://www.zzvips.com/article/201157.html
# 引入模块
import pymysql
# 创建一个连接对象
connection = pymysql.connect(
    host='localhost',
    port=3306,  # 注意: 端口后一定是整型
    user='root',
    password='mysql123456',
    # database='my_test', #这里可以直接指定数据库
    charset='utf8'  # 注意:此处是utf8, 不是utf-8
)


# with connection.cursor() as cur:
#     cur.execute('执行SQL语句')
# 创建一个游标对象 ---> 游标对象是通过连接对象去创建的
cur = connection.cursor()

#创建数据库or指定数据库
# 创建数据库的sql(如果数据库存在就不创建，防止异常)
# sql = "CREATE DATABASE IF NOT EXISTS db_name"
sql = "CREATE DATABASE IF NOT EXISTS my_test;"
# 执行创建数据库的sql
cur.execute(sql)
#指定数据库
sql="use my_test;"
cur.execute(sql)

#创建表
# 如果该表存在就删除
cur.execute("drop table if exists test_pymsql;")
# 定义sql语句
sql = """ CREATE TABLE `test_pymsql` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name` varchar(20) DEFAULT NULL COMMENT '姓名',
  `department` varchar(20) DEFAULT NULL COMMENT '部门',
  `salary` decimal(10,2) DEFAULT NULL COMMENT '工资',
  `age` int(11) DEFAULT NULL COMMENT '年龄',
  `sex` varchar(4) DEFAULT NULL COMMENT '性别',
  PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""
# 建表
cur.execute(sql)


#查
# 查看sql语句的执行结果  ---> 通过游标对象去查看
sql="select id, name, department, salary, age, sex from test_pymsql where id>%s and sex=%s;"
try:
    cur.execute(sql, (1, "女"))
    # 获取所有的查询结果 返回一个元组
    resultAll = cur.fetchall()
    print("resultAll:", resultAll)
    # 获取2条数据
    resultTwo = cur.fetchmany(2)
    print("resultTwo:", resultTwo)
    # 获取一条数据
    resultOne = cur.fetchone()
    print("resultThree:", resultOne)
    connection.commit()
    print("sql(select)->success")

except:
    connection.rollback()
    print("sql(select)->error")

#增
# sql = 'insert into table_name(field_list) values(%s)'  # 有几个字段就有几个%s
# cur.execute(sql, value) #操作一条语句
# cur.executemany(sql, values) #操作多条语句

# 定义sql语句
sql = """ insert into test_pymsql (name,department,salary,age,sex) 
values("tom","开发部",8000,25,"男"), ("jari","开发部",8000,25,"男");
"""

# 尝试捕捉错误
try:
    # 执行SQL，并返回收影响行数
    result = cur.execute(sql)
    # 提交事务
    connection.commit()
    print("sql(insert)->success")
except:
    # 如果发生错误 则回滚事务
    print("sql(insert)->error")
    connection.rollback()


#删
# sql = 'delete from table_name where if'
# cur.execute(sql)
# 定义sql
sql = "delete from test_pymsql where id=%s;"
try:
    # 执行一条sql
    cur.execute(sql, (21))
    # 提交事务
    connection.commit()
    print("sql(delete)->success")
except  Exception as e:
    # 回滚事务
    connection.rollback()
    print("sql(delete)->error")
    print(e)

#改
# sql = "update table_name set field_name_list = value"
# cur.execute(sql, value)
# 定义sql
sql="update test_pymsql set salary=%s,name=%s where id=%s;"
# 如果sql错误就执行回滚操作，成功就提交
try:
    # 执行sql，并且返回影响的行数
    result=cur.execute(sql,[6000,"admin",19])
    connection.commit()
    print("sql（update）->success")
except:
    print("sql(update)->error")
    connection.rollback()

#提交事务
# connection.commit()
# 关闭游标
cur.close()
# 关闭数据库连接对象
connection.close()