import backend_functions as B
xb = B.connection()
cur = xb.cursor()
#B.wanttoggle(cur,'Adam','12345')
print(B.wanttoggle(cur,'Adam',False))
#print(bool([]))