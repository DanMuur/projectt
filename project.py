from unicodedata import name
import tornado.web
import asyncio
import os
import sqlite3 as sq
from datetime import datetime

bdpath = "bd/th.sql"

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    "login_url": "/login",
    "autoreload": "True",
}

class Base(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class Main(Base):
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        bas = sq.connect(bdpath)
        bd = bas.cursor()
        bd.execute("""select * from themes""")
        themes = bd.fetchall()
        if not themes:
            themes = [["","нет тем"]]
        bd.close()
        bas.close()
        self.render("templates/themes.html",auth=name,themes=themes)
    @tornado.web.authenticated
    def post(self):
        if not self.get_argument("name"):
            self.get()
            return
        bas = sq.connect(bdpath)
        bd = bas.cursor()
        bd.execute("""select * from themes""")
        themes = bd.fetchall()
        bd.execute("""insert into themes values({},{})""".format(len(themes)+1,"'"+self.get_argument("name")+"'"))
        bas.commit()
        bd.close()
        bas.close()
        self.get()

class Discuss(Base):
    @tornado.web.authenticated
    def get(self,id):
        auth = tornado.escape.xhtml_escape(self.current_user)
        bas = sq.connect(bdpath)
        bd = bas.cursor()
        bd.execute("""select name from themes where id = {}""".format(id))
        name = bd.fetchone()
        bd.close()
        bas.close()
        bas = sq.connect(bdpath)
        bd = bas.cursor()
        bd.execute("""create table if not exists d{}(
            id varchar(4),
            auth varchar(20),
            mes varchar(200),
            data datatime
        )""".format(id))
        bd.execute("""select * from d{}""".format(id))
        mes = bd.fetchall()
        if not mes:
            mes = [["","","нет сообщений",""]]
        bd.close()
        bas.close()
        self.render("templates/discus.html",auth=auth,name=name,messages=mes)
    @tornado.web.authenticated
    def post(self,id):
        name = tornado.escape.xhtml_escape(self.current_user)
        bas = sq.connect(bdpath)
        bd = bas.cursor()
        bd.execute("""select * from d{}""".format(id))
        mess = bd.fetchall()
        bd.execute("""insert into d{} values({},{},{},{})""".format(id,len(mess)+1,"'"+name+"'","'"+self.get_argument("mes")+"'",'"'+datetime.now().strftime("%Y/%m/%d %H:%M:%S")+'"'))
        bas.commit()
        bd.close()
        bas.close()
        self.get(id)
        return

class Login(Base):
    def get(self):
        self.render("templates/login.html")
    def post(self):
        self.set_secure_cookie("user", self.get_argument("name"))
        self.redirect("/")

def make_app():
    return tornado.web.Application([
        (r"/", Main),
        (r"/(..?)", Discuss),
        (r"/login", Login),
    ], **settings)

def db():
    bas = sq.connect(bdpath)
    bd = bas.cursor()
    bd.execute("""create table if not exists themes(
        id varchar(3),
        name varchar(200)
    )""")
    bd.close()
    bas.close()

async def main():
    db()
    app = make_app()
    app.listen(8888)
    print("server is running on")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())