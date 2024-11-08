class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # For PostgreSQL:
    # SQLALCHEMY_DATABASE_URI = 'postgresql://energy_user:securepassword@localhost/energy_tracker_db'
    # For MySQL, uncomment this line:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://energy_user:securepassword@localhost/energy_tracker_db'
