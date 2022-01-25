import os
import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtGui import QCursor
import requests
import urllib.request
#from iso639 import languages
from functools import partial
import backend_functions as bgfns
import mysql.connector as sqltor
con_obj = bgfns.connection()
cur1 = con_obj.cursor()
gbooksapikey = 'AIzaSyAo1J2T3P4d8Wi8lw0xrOG_VaTNW_7Ltck'


class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi('welcome-screen.ui', self)
        self.login_button.clicked.connect(self.gotologin)
        self.new_acc_button.clicked.connect(self.gotocreate)

    @staticmethod
    def gotologin():
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    @staticmethod
    def gotocreate():
        create = CreateAccScreen()
        widget.addWidget(create)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi('login.ui', self)
        self.password_line_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login_button.clicked.connect(self.login_function)
        self.sign_up_button.clicked.connect(WelcomeScreen.gotocreate)
    
    def login_function(self):  # Function to help user log in
        global username
        username = self.username_line_edit.text()  # Username entered by user
        password = self.password_line_edit.text()  # Password entered by user
        if len(username) == 0 or len(password) == 0:  # checks if all fields have been filled
            self.error_label.setText('Please input all fields')
        else:
            try:
                userdata = bgfns.login(cur1,username)
                matched_password = userdata[1]  # Searches for username in SQL. If it doesn't exist then it goes to the except statement, if it does exist then matched password will become required password.
                if matched_password == password:  # Verifies if required password (i.e, matched_password) matches with the password entered by user
                    print('Successfully logged in')
                    main_screen = MainScreen()
                    widget.addWidget(main_screen)
                    widget.setCurrentIndex(widget.currentIndex() + 1)
                else:
                    self.error_label.setText('Invalid username or password')
            except:  # Goes to except if username is not found in database
                self.error_label.setText('Invalid username or password')


class CreateAccScreen(QDialog):
    def __init__(self):
        super(CreateAccScreen, self).__init__()
        loadUi('create-acc.ui', self)
        self.password_line_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_password_line_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.sign_up_button.clicked.connect(self.sign_up_function)
        self.login_button.clicked.connect(WelcomeScreen.gotologin)

    def sign_up_function(self):  # Function to help users create a new account
        global credentials, username
        username = self.username_line_edit.text()  # Username entered by user
        password = self.password_line_edit.text()  # Password entered by user
        confirm_password = self.confirm_password_line_edit.text()  # Password entered again by user
        if len(username) == 0 or len(password) == 0 or len(confirm_password) == 0:  # If all fields haven't been filled throw error
            self.error_label.setText("Please fill in all fields")
        elif password != confirm_password:  # If password does not match confirm password, throw error
            self.error_label.setText("Passwords do not match")
        elif  (bgfns.getuser(username,cur1)) and (username in bgfns.getuser(username,cur1)):  # If username exists throw error
            self.error_label.setText("Username is already taken")
        else:  # Add username-password pair to database
            bgfns.create_profile(username,password,cur1)
            WelcomeScreen().gotologin()


class MainScreen(QDialog):
    def __init__(self):
        super(MainScreen, self).__init__()
        loadUi('main-screen.ui', self)
        self.search_button.clicked.connect(self.search_function)
        self.menu_home.clicked.connect(ButtonRedirect.gotomenu)
        self.menu_fav.clicked.connect(lambda: self.gotouserlists(0))
        self.menu_my_read.clicked.connect(lambda: self.gotouserlists(1))
        self.menu_read_list.clicked.connect(lambda: self.gotouserlists(2))
        self.menu_sign_out.clicked.connect(WelcomeScreen.gotologin)

    def search_function(self):  # Home page search function
        global searchterm
        searchterm = self.search_line_edit.text()
        if len(searchterm):
            QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={searchterm}&maxResults=40&key={gbooksapikey}").json()
            search_screen = SearchScreen(response, True)
            widget.addWidget(search_screen)
            widget.setCurrentIndex(widget.currentIndex() + 1)

    @staticmethod
    def gotouserlists(num):  # Function to redirect users to My read/Favourites/Read list tab
        items = []
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        user_lists = [bgfns.liketoggle(cur1,username,False), bgfns.readtoggle(cur1,username,False), bgfns.readtoggle(cur1,username,False)]
        for book_id in user_lists[num]:
            resp = requests.get(f"https://www.googleapis.com/books/v1/volumes/{book_id}").json()
            items = items + [resp]
        response = {'items': items}
        search_screen = SearchScreen(response, False, num)
        widget.addWidget(search_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class SearchScreen(QDialog):
    def __init__(self, response, search, list_num=0):
        global thumbnail_list, title_list, authors_list, publisher_list, desc_list, lang_list, book_id_list
        super(SearchScreen, self).__init__()
        user_lists = [bgfns.liketoggle(cur1,username,False), bgfns.readtoggle(cur1,username,False), bgfns.readtoggle(cur1,username,False)]
        if search:
            loadUi('search-screen.ui', self)
            self.search_line_edit.setText(searchterm)
            iter_no = 40
        else:
            loadUi('user-list-screen.ui', self)
            iter_no = len(user_lists[list_num])
            if list_num == 1:
                self.title_label.setText('My Read')
                self.setWindowTitle('My Read')
            elif list_num == 2:
                self.title_label.setText('Read List')
                self.setWindowTitle('Read List')
        j = 0
        thumbnail_list = title_list = authors_list = publisher_list = desc_list = lang_list = book_id_list = []
        for i in range(iter_no):
            try:
                book_info = response['items'][i]
            except:
                break
            try:
                book_id = book_info['id']
                title = book_info['volumeInfo']['title']
                thumbnail = book_info['volumeInfo']['imageLinks']['thumbnail']
                authors = ', '.join(book_info['volumeInfo']['authors'])
                desc = book_info['volumeInfo']['description']
                lang = "English"
            except:
                continue
            try:
                publisher = book_info['volumeInfo']['publisher']
            except:
                publisher = 'Centry Publication House'
            # Thumbnail label
            self.label = QtWidgets.QLabel(self.bgwidget)
            self.label.setGeometry(QtCore.QRect(100 + ((j % 5) * 200), 210 + ((j // 5) * 300), 128, 190))
            self.label.setText('')
            image = QtGui.QImage()
            image.loadFromData(urllib.request.urlopen(thumbnail).read())
            self.label.setPixmap(QtGui.QPixmap(image))
            self.label.setScaledContents(True)
            self.label.setObjectName("label_book_" + str(j + 1))
            # Book title label
            self.plainTextEdit = QtWidgets.QPlainTextEdit(self.bgwidget)
            self.plainTextEdit.setGeometry(QtCore.QRect(100 + ((j % 5) * 200), 400 + ((j // 5) * 300), 128, 87))
            self.plainTextEdit.setStyleSheet("background-color: rgba(0, 0, 0, 0);"
                                             "color: white;"
                                             "border: None;"
                                             "font: 9pt \"MS Shell Dlg 2\";")
            self.plainTextEdit.setObjectName("plain_text_book_" + str(j + 1))
            self.plainTextEdit.setPlainText(QtCore.QCoreApplication.translate("Dialog", title))
            # Book redirect buttons
            self.button = QtWidgets.QPushButton(self.bgwidget)
            self.button.setGeometry(QtCore.QRect(100 + ((j % 5) * 200), 210 + ((j // 5) * 300), 128, 190))
            self.button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
            self.button.setText("")
            self.button.setObjectName("button_book_" + str(j + 1))
            self.button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
            thumbnail_list = thumbnail_list + [thumbnail]
            title_list = title_list + [title]
            authors_list = authors_list + [authors]
            publisher_list = publisher_list + [publisher]
            desc_list = desc_list + [desc]
            lang_list = lang_list + [lang]
            book_id_list = book_id_list + [book_id]
            j += 1
        error_dialog = QtWidgets.QErrorMessage()
        error_dialog.showMessage('Oh no!')

        if not title_list:
            self.error_label = QtWidgets.QLabel(self.bgwidget)
            self.error_label.setGeometry(QtCore.QRect(0, 320, 1171, 131))
            self.error_label.setAlignment(QtCore.Qt.AlignCenter)
            self.error_label.setStyleSheet("font: 16pt \"Roboto\";\n"
                                           "color: rgb(255, 0, 0);")
            self.error_label.setObjectName("error_label")
            if search:
                self.error_label.setText(QtCore.QCoreApplication.translate("Dialog", "No results containing your search term were found"))
            else:
                self.error_label.setText(
                    QtCore.QCoreApplication.translate("Dialog", "No books added"))
        elif len(title_list) > 10:
            self.scrollAreaWidgetContents.resize(1200, 1150 + (len(title_list) - 11) // 5 * 300)
            self.bgwidget.resize(1200, 1150 + (len(title_list) - 11) // 5 * 300)
        QApplication.restoreOverrideCursor()
        if search:
            self.search_button.clicked.connect(self.search_function)
        for button in self.bgwidget.findChildren(QtWidgets.QPushButton):
            button.clicked.connect(partial(self.check_clicked))
        self.menu_home.clicked.connect(ButtonRedirect.gotomenu)
        self.menu_fav.clicked.connect(lambda: self.gotouserlists(0))
        self.menu_my_read.clicked.connect(lambda: self.gotouserlists(1))
        self.menu_read_list.clicked.connect(lambda: self.gotouserlists(2))
        self.menu_sign_out.clicked.connect(WelcomeScreen.gotologin)

    def search_function(self):
        global searchterm
        searchterm = self.search_line_edit.text()
        if len(searchterm):
            QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={searchterm}&maxResults=40&key={gbooksapikey}").json()
            search_screen = SearchScreen(response, True)
            widget.addWidget(search_screen)
            widget.setCurrentIndex(widget.currentIndex() + 1)

    def check_clicked(self):
        try:
            button_redirect = ButtonRedirect(int((self.sender().objectName())[12:]) - 1)
            widget.addWidget(button_redirect)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        except:
            pass

    @staticmethod
    def gotouserlists(num):
        items = []
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        user_lists = [bgfns.liketoggle(cur1,username,False), bgfns.readtoggle(cur1,username,False), bgfns.readtoggle(cur1,username,False)]
        for book_id in user_lists[num]:
            resp = requests.get(f"https://www.googleapis.com/books/v1/volumes/{book_id}").json()
            items = items + [resp]
        response = {'items': items}
        search_screen = SearchScreen(response, False, num)
        widget.addWidget(search_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class ButtonRedirect(QDialog):#TODO: get temp book inserted
    def __init__(self, button_num):
        super(ButtonRedirect, self).__init__()
        loadUi('expanded-book.ui', self)
        _translate = QtCore.QCoreApplication.translate
        # Thumbnail
        self.book_thumbnail = QtWidgets.QLabel(self.bgwidget)
        self.book_thumbnail.setGeometry(QtCore.QRect(70, 70, 320, 475))
        self.book_thumbnail.setText("")
        image = QtGui.QImage()
        image.loadFromData(urllib.request.urlopen(thumbnail_list[button_num]).read())
        self.book_thumbnail.setPixmap(QtGui.QPixmap(image))
        self.book_thumbnail.setScaledContents(True)
        self.book_thumbnail.setObjectName("book_thumbnail")
        # Title
        self.book_title = QtWidgets.QPlainTextEdit(self.bgwidget)
        self.book_title.setGeometry(QtCore.QRect(450, 90, 631, 87))
        self.book_title.setStyleSheet("color: #f0f0f0;\n"
                                      "font: 15pt \"MS Shell Dlg 2\";\n"
                                      "background-color: rgba(0, 0, 0, 0);\n"
                                      "border: None;")
        self.book_title.setObjectName("book_title")
        # Description
        self.book_description = QtWidgets.QPlainTextEdit(self.bgwidget)
        self.book_description.setGeometry(QtCore.QRect(440, 380, 731, 401))
        self.book_description.setStyleSheet("color: #ebebeb;\n"
                                            "font: 15pt \"MS Shell Dlg 2\";\n"
                                            "background-color: rgba(0, 0, 0, 0);\n"
                                            "border: None;")
        self.book_description.setObjectName("book_description")
        # Comments
        self.Comment_as_label.setText(f'Comment as {username}')
        try:  # Checks if comments for particular book exist else goes to except
            comments_list = bgfns.insertcomment(cur1,book_id_list[button_num],False)
            self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1198, 1100 + (170 * len(comments_list))))
            self.bgwidget.setGeometry(QtCore.QRect(0, 0, 1198, 1100 + (170 * len(comments_list))))
            for i in range(len(comments_list)):
                self.comment = QtWidgets.QPlainTextEdit(self.bgwidget)
                self.comment.setGeometry(QtCore.QRect(170, 1140 + (150 * i), 931, 91))
                self.comment.setStyleSheet("background-color: #00000000;\n"
                                           "border: None;\n"
                                           "color: white;\n"
                                           "font: 10pt \"MS Shell Dlg 2\";")
                self.comment.setObjectName(f"comment_{i + 1}")
                self.default_avatar = QtWidgets.QLabel(self.bgwidget)
                self.default_avatar.setGeometry(QtCore.QRect(70, 1100 + (150 * i), 71, 71))
                self.default_avatar.setText("")
                self.default_avatar.setPixmap(QtGui.QPixmap("assets/default avatar.png"))
                self.default_avatar.setScaledContents(True)
                self.default_avatar.setObjectName(f"default_avatar_{i + 1}")
                self.username = QtWidgets.QLabel(self.bgwidget)
                self.username.setGeometry(QtCore.QRect(175, 1110 + (150 * i), 1061, 21))
                self.username.setStyleSheet("color: rgb(238, 2, 73);\n"
                                            "font: 10pt \"MS Shell Dlg 2\";")
                self.username.setObjectName(f"username_{i + 1}")
                self.comment.setPlainText(_translate("Dialog", comments_list[i][1]))
                self.username.setText(_translate("Dialog", comments_list[i][0]))
                if username in admin_list or username == comments_list[i][0]:
                    self.remove_icon = QtWidgets.QLabel(self.bgwidget)
                    self.remove_icon.setGeometry(QtCore.QRect(740, 1110 + (150 * i), 20, 20))
                    self.remove_icon.setText("")
                    self.remove_icon.setPixmap(QtGui.QPixmap("assets/remove_icon1.png"))
                    self.remove_icon.setScaledContents(True)
                    self.remove_icon.setObjectName(f"remove_icon_{i + 1}")
                    self.remove_text = QtWidgets.QLabel(self.bgwidget)
                    self.remove_text.setGeometry(QtCore.QRect(770, 1110 + (150 * i), 61, 20))
                    self.remove_text.setStyleSheet("color: white; font: 10pt \"MS Shell Dlg 2\";")
                    self.remove_text.setObjectName(f"remove_text_{i + 1}")
                    self.remove_text.setText(_translate("Dialog", "Remove"))
                    self.remove_button = QtWidgets.QPushButton(self.bgwidget)
                    self.remove_button.setGeometry(QtCore.QRect(740, 1110 + (150 * i), 91, 21))
                    self.remove_button.setStyleSheet("#remove_button_" + str(i + 1) + " {background-color: #00000000;}")
                    self.remove_button.setText("")
                    self.remove_button.setObjectName(f"remove_button_{i + 1}")
                    self.remove_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                    if username in admin_list:
                        self.ban_icon = QtWidgets.QLabel(self.bgwidget)
                        self.ban_icon.setGeometry(QtCore.QRect(860, 1110 + (150 * i), 23, 23))
                        self.ban_icon.setText("")
                        self.ban_icon.setPixmap(QtGui.QPixmap("assets/ban_icon.png"))
                        self.ban_icon.setScaledContents(True)
                        self.ban_icon.setObjectName(f"ban_icon_{i + 1}")
                        self.ban_text = QtWidgets.QLabel(self.bgwidget)
                        self.ban_text.setGeometry(QtCore.QRect(890, 1110 + (150 * i), 71, 20))
                        self.ban_text.setStyleSheet("color: white; font: 10pt \"MS Shell Dlg 2\";")
                        self.ban_text.setObjectName(f"ban_text_{i + 1}")
                        self.ban_text.setText(_translate("Dialog", "Ban User"))
                        self.ban_button = QtWidgets.QPushButton(self.bgwidget)
                        self.ban_button.setGeometry(QtCore.QRect(860, 1110 + (150 * i), 101, 21))
                        self.ban_button.setStyleSheet("#ban_button_" + str(i + 1) + " {background-color: #00000000;}")
                        self.ban_button.setText("")
                        self.ban_button.setObjectName(f"ban_button_{i + 1}")
                        self.ban_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        except:
            pass

        # Translation
        self.book_title.setPlainText(_translate("Dialog", title_list[button_num]))
        self.book_description.setPlainText(_translate("Dialog", desc_list[button_num]))
        self.book_publisher.setText(_translate("Dialog", "Publisher: " + publisher_list[button_num]))
        self.book_author.setText(_translate("Dialog", "Author: " + authors_list[button_num]))
        self.book_language.setText(_translate("Dialog", "Language: " + lang_list[button_num]))
        self.fav_button.setText(_translate("Dialog", "Add to Favourites"))
        self.my_read_button.setText(_translate("Dialog", "Add to My Read"))
        self.read_list_button.setText(_translate("Dialog", "Add to Read List"))
        # Button highlight
        button_clicked_style = 'border-radius: 5px;' \
                               'font: 14pt "MS Shell Dlg 2";' \
                               'color: rgb(255, 255, 255);' \
                               'border: 1px solid rgb(238, 2, 73);' \
                               'background-color: rgb(238, 2, 73);'
        if book_id_list[button_num] in bgfns.liketoggle(cur1,username,False):
            self.fav_button.setStyleSheet(button_clicked_style)
        if book_id_list[button_num] in bgfns.readtoggle(cur1,username,False):
            self.my_read_button.setStyleSheet(button_clicked_style)
        if book_id_list[button_num] in bgfns.readtoggle(cur1,username,False):
            self.read_list_button.setStyleSheet(button_clicked_style)
        # Menu
        self.menu_home.clicked.connect(self.gotomenu)
        self.menu_fav.clicked.connect(lambda: self.gotouserlists(0))
        self.menu_my_read.clicked.connect(lambda: self.gotouserlists(1))
        self.menu_read_list.clicked.connect(lambda: self.gotouserlists(2))
        self.menu_sign_out.clicked.connect(WelcomeScreen.gotologin)
        self.back_icon_button.clicked.connect(self.goback)
        self.fav_button.clicked.connect(lambda: self.edit_fav_list(button_num))
        self.my_read_button.clicked.connect(lambda: self.edit_my_read_list(button_num))
        self.read_list_button.clicked.connect(lambda: self.edit_read_list(button_num))

        self.comment_submit_button.clicked.connect(lambda: self.add_comment(button_num))

    @staticmethod
    def gotomenu():
        main_screen = MainScreen()
        widget.addWidget(main_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    @staticmethod
    def goback():
        widget.removeWidget(widget.currentWidget())

    def edit_fav_list(self, num):
        if book_id_list[num] in bgfns.liketoggle(cur1,username,False):  # Check if book is in fav_list
            bgfns.liketoggle(cur1,username,True,book_id_list[num])
            
            self.fav_button.setStyleSheet('border-radius: 5px;'
                                          'font: 14pt "MS Shell Dlg 2";'
                                          'color: rgb(255, 255, 255);'
                                          'border: 1px solid rgb(238, 2, 73);')
        else:
            bgfns.liketoggle(cur1,username,True,book_id_list[num])
            self.fav_button.setStyleSheet('border-radius: 5px;'
                                          'font: 14pt "MS Shell Dlg 2";'
                                          'color: rgb(255, 255, 255);'
                                          'border: 1px solid rgb(238, 2, 73);'
                                          'background-color: rgb(238, 2, 73);')

    def edit_my_read_list(self, num):
        if book_id_list[num] in bgfns.wanttoggle(cur1,username,False):
            bgfns.readtoggle(cur1,username,True,book_id_list[num])
            self.my_read_button.setStyleSheet('border-radius: 5px;'
                                              'font: 14pt "MS Shell Dlg 2";'
                                              'color: rgb(255, 255, 255);'
                                              'border: 1px solid rgb(238, 2, 73);')
        else:
            bgfns.readtoggle(cur1,username,True,book_id_list[num])
            self.my_read_button.setStyleSheet('border-radius: 5px;'
                                              'font: 14pt "MS Shell Dlg 2";'
                                              'color: rgb(255, 255, 255);'
                                              'border: 1px solid rgb(238, 2, 73);'
                                              'background-color: rgb(238, 2, 73);')

    def edit_read_list(self, num):
        if book_id_list[num] in bgfns.readtoggle(cur1,username,False):
            bgfns.wanttoggle(cur1,username,True,book_id_list[num])
            self.read_list_button.setStyleSheet('border-radius: 5px;'
                                                'font: 14pt "MS Shell Dlg 2";'
                                                'color: rgb(255, 255, 255);'
                                                'border: 1px solid rgb(238, 2, 73);')
        else:
            bgfns.wanttoggle(cur1,username,True,book_id_list[num])
            self.read_list_button.setStyleSheet('border-radius: 5px;'
                                                'font: 14pt "MS Shell Dlg 2";'
                                                'color: rgb(255, 255, 255);'
                                                'border: 1px solid rgb(238, 2, 73);'
                                                'background-color: rgb(238, 2, 73);')

    @staticmethod
    def gotouserlists(num):
        items = []
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        user_lists = [bgfns.liketoggle(cur1,username,False), bgfns.readtoggle(cur1,username,False), bgfns.readtoggle(cur1,username,False)]
        for book_id in user_lists[num]:
            resp = requests.get(f"https://www.googleapis.com/books/v1/volumes/{book_id}").json()
            items = items + [resp]
        response = {'items': items}
        search_screen = SearchScreen(response, False, num)
        widget.addWidget(search_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def add_comment(self, num):
        comment = self.comment_input_text_edit.toPlainText()  # Gets comment from user and stores it into the 'comment' var
        bgfns.insertcomment(cur1,book_id_list[num],True,username,comment)
        widget.addWidget(ButtonRedirect(num))
        widget.setCurrentIndex(widget.currentIndex() + 1)


# main
# replace fav_list, book_id_list, my_read_list, read_list, comments_dict, credentials
thumbnail_list = title_list = authors_list = publisher_list = desc_list = lang_list  = book_id_list = []
comments_dict = {'id': [('Name', 'Comment')]}
admin_list = ['root']
username = searchterm = ''
if __name__ == '__main__':
    app = QApplication(sys.argv)
    welcome = WelcomeScreen()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(welcome)
    widget.setFixedHeight(800)
    widget.setFixedWidth(1200)
    widget.show()
    try:
        sys.exit(app.exec_())
    except:
        print('Exiting')
        bgfns.eradicate()
