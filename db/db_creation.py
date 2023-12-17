#pip install python-dotenv
#pip install pymysql
#pip install sqlalchemy
import os
from sqlalchemy import create_engine, inspect, Column, Integer, String, Date, ForeignKey, text
from sqlalchemy.orm import relationship, Session, declarative_base
from dotenv import load_dotenv

load_dotenv('.env')

Base = declarative_base()

class ndc(Base):
    __tablename__ = 'drugs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_ndc = Column(String(500), nullable=True)
    generic_name = Column(String(500), nullable=True)
    labeler_name = Column(String(500), nullable=True)
    brand_name = Column(String(500), nullable=True)
    dosage_form = Column(String(500), nullable=True)
    route = Column(String(500), nullable=True)
    brand_name_base = Column(String(500), nullable=True)
    dea_schedule = Column(String(500), nullable=True)
       
### Part 2 - initial sqlalchemy-engine to connect to db:

# Database connection settings from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_CHARSET = os.getenv("DB_CHARSET", "utf8mb4")

# Connection string
conn_string = (
    f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    f"?charset={DB_CHARSET}"
)

# Create a database engine
db_engine = create_engine(conn_string, echo=False)

## Test connection

inspector = inspect(db_engine)
inspector.get_table_names()

### Part 3 - create the tables using sqlalchemy models, with no raw SQL required:

Base.metadata.create_all(db_engine)
