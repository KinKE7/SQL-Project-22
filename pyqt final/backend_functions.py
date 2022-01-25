import mysql.connector as sqltor
import pickle as binwriter

def locpwd(bool = False):                           #password storage for user's root login, stores password in assets\pwd.bin
    #f = open('pwd.bin','rb')
    password = ('scamper@8',)                  #pickler for the binary file
    #f.close()
    if password[0] == '' or bool:                   #prompts user to enter his root password, incase the password is incorrect or missing
        print("Your password for MySQL root is missing. Please type it in so that the application may access it without any hassles.")
        f = open('pwd.bin','wb')                    # Sujal : (might want a popup for the visual PyQt dialog)
        password[0] = input("please enter your password for MySQL root: ") # make a prompt for the application
        binwriter.dump(password,f)
        f.close()
        return None                                 #ensures the last return statement is not executed in case of incorrect password
    return password[0]

def connection():                        
    mycon = sqltor.connect(host = "localhost",
                           user = 'root',
                           password = locpwd(),
                           database = 'bookipedia')
    if mycon.is_connected():
        return mycon
    else:
        locpwd(True)
        connection()


def create_profile(uname,pwd,xursor):               #xursor : connection object init from main.py
    xursor.execute("use BookiPedia")
    xursor.execute('insert into registry VALUES("%s","%s");'%(uname,pwd))
    xursor.execute("commit;")

def getuser(name,cur):
    cur.execute("SELECT name FROM registry where name = '%s';"%(name))
    D = cur.fetchone()
    return(D)
    
# need to create an admin profile interface that only shows the book readers (No books, only list of names and options to perform  admin functions)

def delete_profile(name):
    myc = connection()
    admin_cur = myc.connection()
    admin_cur.execute("use BookiPedia")
    admin_cur.execute('delete from regdata where name = "%s";'%(name))
    admin_cur.execute('delete from registry where name = "%s";'%(name))
    admin_cur.execute('commit;')


# Password change function for login (only admin access) (need to create)

def login(xursor,uname):
    xursor.execute("use BookiPedia")
    xursor.execute('select * from registry where name = "%s";'%(uname))    # might have to change the database name later to a password manager later
    U_Query = xursor.fetchone()       #gives tuple : [0] = name, [1] = password , if not found returns NoneType
    return U_Query
        
        
            
    

#offensive comment delete
def offensive_comment(xursor,uname,bookid):
    xursor.execute("use BookiPedia")
    xursor.execute("")                          #comment remover goes here (will probably replace with "this message was deleted by admins for being offensive")
    return None
#------------------------------------------------------------------------------------------------------------------------------

#CONDITIONAL FUNCTION WE NEEED TO EXTRACT THE USERNAME AND BOOKNAME TO PROVIDE THE INPUT FOR
# legend:
# 0 - tempbook (deleted on exiting the application)
# 1 - set book as liked
# 2 - set book as read
# 3 - set book as want to read
#------------------------------------------------------------------------------------------------------------------------------
def tempbook(cur,uname,bookid = '',codn = True):
    cur.execute('insert into regdata (name,book) values("%s","%s");'%(uname,bookid))
    cur.execute('commit;')

def liketoggle(cur,uname,condn = True,bookid = ''):
    if condn:
        cur.execute('select likebook from regdata where name = "%s" and book = "%s";'%(uname,bookid))
        likebool = cur.fetchone()[0]
        if not likebool:
            likebool = 1
        else:
            likebool = 0
        cur.execute('update regdata SET likebook = %s where name = "%s" and book="%s";'%(likebool,uname,bookid))
        cur.execute('commit;')
    else:
        cur.execute('select book from regdata where likebook = 1 and name = "%s";'%(uname))
        returnlist = cur.fetchall()
        if bool(returnlist):
            return list(i[0] for i in returnlist)
        else:
            return []

def readtoggle(cur,uname,condn = True,bookid = ''):
    if condn:
        cur.execute('select readbook from regdata where name = "%s" and book = "%s";'%(uname,bookid))
        readbool = cur.fetchone()[0]
        if not readbool:
            readbool = 1
        else:
            readbool = 0
        cur.execute('update regdata SET readbook = %s where name = "%s" and book="%s";'%(readbool,uname,bookid))
        cur.execute('commit;')
    else:
        cur.execute('select book from regdata where readbook = 1 and name = "%s";'%(uname))
        returnlist = cur.fetchall()
        if bool(returnlist):
            return list(i[0] for i in returnlist)
        else:
            return []

def wanttoggle(cur,uname,condn = True,bookid = ''):
    if condn:
        cur.execute('select wantbook from regdata where name = "%s" and book = "%s";'%(uname,bookid))
        wantbool = cur.fetchone()[0]
        if not wantbool:
            wantbool = 1
        else:
            wantbool = 0
        cur.execute('update regdata SET wantbook = %s where name = "%s" and book="%s";'%(wantbool,uname,bookid))
        cur.execute('commit;')
    else:
        cur.execute('select book from regdata where wantbook = 1 and name = "%s";'%(uname))
        returnlist = cur.fetchall()
        if bool(returnlist):
            return list(i[0] for i in returnlist)
        else:
            return []

def insertcomment(cur,bookid,condn = True,uname = '',comment = ''):
    if condn:
        cur.execute('update regdata set comment = "%s" where name = "%s" and book = "%s";'%(comment,uname,bookid))
        cur.execute('commit;')
    else:
        cur.execute('select name,comment from regdata where book = %s'%(bookid))
        D = cur.fetchall()
        print(D)
    
def book_onclick(name,book,cur,case = 1,click = True):
    if case == 1:
        if click:
            cur.execute('select likebook from regdata where name = "%s" and book = "%s";'%(name,book))
            lb = bool(cur.fetchone()[0])
            cur.execute('update regdata SET likebook = %s where name = "%s" and book="%s";'%(int(not lb),name,book))
            cur.execute('commit;')
#------------------------------------------------------------------------------------------------------------------------------
#at end of every session, remove all books which are still not favourited/read/want to read... those books will not exist for the user's sql table
#------------------------------------------------------------------------------------------------------------------------------
def eradicate():
    myc = connection()
    admin_cur = myc.connection()
    admin_cur.execute("use BookiPedia")
    admin_cur.execute("delete from regdata where readbook + likebook + wantbook = 0;")
    admin_cur.execute('commit;')

def getcount(xursor,book,case = 0):                   #get counts of liked/read/want to read and display them with the book
    pass                   