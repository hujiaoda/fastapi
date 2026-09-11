from sqlalchemy import create_engine
from config import DB_URI


engine = create_engine(
    
    DB_URI, 
    #输出日志
    echo=True,
    #最大连接数
    pool_size=10, 
    #额外的连接数
    max_overflow=20, 
    #连接池中连接的最大空闲时间，单位为秒
    pool_recycle=3600,
    
    pool_pre_ping=True
)