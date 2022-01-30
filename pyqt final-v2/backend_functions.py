import mysql.connector as sqltor
import pickle as binwriter


def initialise_sql(host, user, password):  # password storage for user's root login, stores password in assets\pwd.bin
    try:
        mycon = sqltor.connect(host=host,
                               user=user,
                               password=password)
    except:
        return False
    with open('creds.bin', 'wb') as f:
        binwriter.dump({'host': host, 'user': user, 'password': password}, f)
    cur = mycon.cursor()
    try:
        cur.execute("drop database bookipedia")
    except:
        pass
    cur.execute('create database bookipedia')
    cur.execute('use bookipedia')
    cur.execute('''create table registry(
    name varchar(20) not null,
    password varchar(20) not null);''')
    cur.execute('''create table regdata(
    name varchar(20) not null,
    book varchar(60),
    readbook bit(1) default b'0',
    likebook bit(1) default b'0',
    wantbook bit(1) default b'0',
    comments varchar(200));''')
    cur.execute('insert into registry VALUES("root","pass");')
    cur.execute("commit;")
    return True


def connection():
    with open('creds.bin', 'rb') as f:
        creds = binwriter.load(f)
    mycon = sqltor.connect(host=creds['host'],
                           user=creds['user'],
                           password=creds['password'],
                           database='bookipedia')
    if mycon.is_connected():
        return mycon


def create_profile(uname, pwd, xursor):  # xursor : connection object init from main.py
    xursor.execute('insert into registry VALUES("%s","%s",0);'%(uname, pwd))
    xursor.execute("commit;")


def getuser(name, cur):
    cur.execute("SELECT name FROM registry where name = '%s';" % name)
    d = cur.fetchone()
    return d


# need to create an admin profile interface that only shows the book readers (No books, only list of names and options to perform  admin functions)

def delete_profile(name):
    myc = connection()
    admin_cur = myc.connection()
    admin_cur.execute("use BookiPedia")
    admin_cur.execute('delete from regdata where name = "%s";' % name)
    admin_cur.execute('delete from registry where name = "%s";' % name)
    admin_cur.execute('commit;')


# Password change function for login (only admin access) (need to create)

def login(xursor, uname):
    xursor.execute("use BookiPedia")
    xursor.execute('select * from registry where name = "%s";' % (
        uname))  # might have to change the database name later to a password manager later
    u_query = xursor.fetchone()  # gives tuple : [0] = name, [1] = password , if not found returns NoneType
    if u_query == None:
        return ['','']
    return u_query


# offensive comment delete
def offensive_comment(xursor, uname, bookid):
    xursor.execute("use BookiPedia")
    xursor.execute(
        "")  # comment remover goes here (will probably replace with "this message was deleted by admins for being offensive")
    return None


# ------------------------------------------------------------------------------------------------------------------------------

# CONDITIONAL FUNCTION WE NEEED TO EXTRACT THE USERNAME AND BOOKNAME TO PROVIDE THE INPUT FOR
# legend:
# 0 - tempbook (deleted on exiting the application)
# 1 - set book as liked
# 2 - set book as read
# 3 - set book as want to read
# ------------------------------------------------------------------------------------------------------------------------------
def tempbook(cur, uname, bookid='', codn=True):
    cur.execute('insert into regdata (name,book) values("%s","%s");' % (uname, bookid))
    cur.execute('commit;')


def liketoggle(cur, uname, condn=True, bookid=''):
    if condn:
        cur.execute('select likebook from regdata where name = "%s" and book = "%s";' % (uname, bookid))
        likebool = cur.fetchone()[0]
        if not likebool:
            likebool = 1
        else:
            likebool = 0
        cur.execute('update regdata SET likebook = %s where name = "%s" and book="%s";' % (likebool, uname, bookid))
        cur.execute('commit;')
    else:
        cur.execute('select book from regdata where likebook = 1 and name = "%s";' % uname)
        returnlist = cur.fetchall()
        if bool(returnlist):
            return list(i[0] for i in returnlist)
        else:
            return []


def readtoggle(cur, uname, condn=True, bookid=''):
    if condn:
        cur.execute('select readbook from regdata where name = "%s" and book = "%s";' % (uname, bookid))
        readbool = cur.fetchone()[0]
        if not readbool:
            readbool = 1
        else:
            readbool = 0
        cur.execute('update regdata SET readbook = %s where name = "%s" and book="%s";' % (readbool, uname, bookid))
        cur.execute('commit;')
    else:
        cur.execute('select book from regdata where readbook = 1 and name = "%s";' % uname)
        returnlist = cur.fetchall()
        if bool(returnlist):
            return list(i[0] for i in returnlist)
        else:
            return []


def wanttoggle(cur, uname, condn=True, bookid=''):
    if condn:
        cur.execute('select wantbook from regdata where name = "%s" and book = "%s";' % (uname, bookid))
        try:
            wantbool = cur.fetchone()[0]
        except TypeError:
            wantbool = 0
        if not wantbool:
            wantbool = 1
        else:
            wantbool = 0
        cur.execute('update regdata SET wantbook = %s where name = "%s" and book="%s";' % (wantbool, uname, bookid))
        cur.execute('commit;')
    else:
        cur.execute('select book from regdata where wantbook = 1 and name = "%s";' % uname)
        returnlist = cur.fetchall()
        if bool(returnlist):
            return list(i[0] for i in returnlist)
        else:
            return []


def insertcomment(cur, bookid, condn=True, uname='', comment=''):
    if condn:
        cur.execute('update regdata set comments = "%s" where name = "%s" and book = "%s";' % (comment, uname, bookid))
        cur.execute('commit;')
    else:
        cur.execute('select name,comments from regdata where book = "%s"' % bookid)
        d = cur.fetchall()
        q = []
        for i in d:
            if bool(i[1]):
                q += [i]       
        return q


def book_onclick(name, book, cur):
    cur.execute("select name,book from regdata where name = '%s' and book = '%s';"%(name,book))
    G = cur.fetchone()
    if G == None:
        cur.execute("insert  into regdata values('%s','%s',0,0,0,'');"%(name,book))
        cur.execute('commit;')

#TODO BANLIST RETURN T RUE LINE 164
#TODO LINE 207,213,216
def banlist(cur):
    cur.execute("select name,bancheck from registry;")
    D = cur.fetchall()
    for i in range(len(D)):
        if D[i][1] == 0:
            D[i] = (D[i][0],False)
        else:
            D[i] = (D[i][0],True)
    return D

    
def ban(uname,cur,banbool = 1):
    cur.execute("update registry set bancheck = %s where name = '%s';"%(banbool,uname))
    cur.execute('commit;')
#------------------------------------------------------------------------------------------------------------------------------
# at end of every session, remove all books which are still not favourited/read/want to read... those books will not exist for the user's sql table
# ------------------------------------------------------------------------------------------------------------------------------
def eradicate():
    myc = connection()
    admin_cur = myc.cursor()
    admin_cur.execute("use BookiPedia")
    admin_cur.execute("delete from regdata where readbook + likebook + wantbook = 0 and comment = '';")
    admin_cur.execute('commit;')


def getcount(xursor, book, case=0):  # get counts of liked/read/want to read and display them with the book
    pass
