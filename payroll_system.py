from db import*
def employee_report():
    cursor.execute("select * from employee")
    data=cursor.fetchall()
    for i in data:
        print(i)

def payroll_report():
    cursor.execute("select * from payroll")
    data=cursor.fetchall()
    for i in data:
        print(i)

def highest_salary():
    cursor.execute("select * from employee order by basic_salary desc limit 1")
    print(cursor.fetchone())

def department_report():
    dept=input("Enter Department : ")
    sql="select * from employee where department=%s"
    value=(dept,)
    cursor.execute(sql, value)
    data=cursor.fetchall()
    for i in data:
        print(i)