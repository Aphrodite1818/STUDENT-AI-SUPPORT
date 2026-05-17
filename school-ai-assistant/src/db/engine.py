#==========================#
# DATABASE ENGINE SETUP    #
#==========================#



from venv import create

from sqlalchemy.ext.asyncio import create_async_engine
from core.config import get_settings
from sqlalchemy.ext.asyncio import async_sessionmaker , AsyncSession

settings = get_settings()

engine = create_async_engine(
    settings.SUPABASE_URL,
    echo = True if settings.ENV == "dev" else False,
    pool_pre_ping = True , 
    
)

AsyncSessionLocal = async_sessionmaker(
    bind = engine , 
    class_ = AsyncSession,
    expire_on_commit=False

)




