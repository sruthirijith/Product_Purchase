from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
# from ..core.api.users import models
import sqlalchemy

DB_URL = ''

metadata = sqlalchemy.MetaData()

engine = create_engine(DB_URL)

metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db = Session()

def truncation(table):
    db.execute(f'''TRUNCATE TABLE {table} RESTART IDENTITY CASCADE''')
    db.commit()
    db.close()
    return True

def update_blocked(table,id):
    # db.query(models.Users).filter(models.Users.id==id).update({"blocked" : True})
    db.execute(f''' UPDATE {table} SET "blocked" = TRUE WHERE id = {id}''')
    db.commit()
    db.close()
    return True

def update_deleted(table,id):
    # db.query(models.Users).filter(models.Users.id==id).update({"deleted" : True})
    db.execute(f''' UPDATE {table} SET "deleted" = TRUE WHERE id = {id}''')
    db.commit()
    db.close()
    return True