import os 


class Config:
    SECRET_KEY = '260fa31c72684ad278f65cac9702'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///C:\\Users\\carlo\\Documents\\nutrideli\\instance\\site.db'  # La ruta buena
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///instance\site.db' 
    #SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')


    # SQLALCHEMY_DATABASE_URI = 'sqlite:///C:/Users/carlo/Documents/nutrideli/instance/site.db'
    # db_path = os.getenv('DB_PATH', 'instance/site.db')


    
    #basedir = os.path.abspath(os.path.dirname(__file__))
    #DB_PATH = os.path.join(basedir, 'instance', 'site.db')
    #DB_PATH = 'instance/site.db'
    #print('RUTA QUE SE ESTA USANDO: ', DB_PATH)
    #SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"



    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')