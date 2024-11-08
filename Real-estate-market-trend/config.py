class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # For PostgreSQL:
    # SQLALCHEMY_DATABASE_URI = 'postgresql://real_estate_user:securepassword@localhost/real_estate_db'
    # For MySQL, use:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://real_estate_user:securepassword@localhost/real_estate_db'
