from uuid import UUID
from sqlalchemy import select , func 
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.subjects.models import Subject


class SubjectRepository:
    """Low-level database queries for the subjects table."""

    @staticmethod
    async def create_subject(db:AsyncSession , subject : Subject) -> Subject:
        db.add(subject)
        await db.flush()
        await db.refresh(subject)
        return subject



    @staticmethod
    async def get_subject_by_id(db: AsyncSession , tenant_id : UUID, subject_id : UUID) -> Subject | None:
        result = await db.execute(
            select(Subject).where(Subject.tenant_id == tenant_id ,Subject.id == subject_id)
        )
        
        return result.scalar_one_or_none()


    
    @staticmethod
    async def get_subject_by_name(db: AsyncSession , tenant_id : UUID , subject_name : str) -> Subject | None:
        result = await db.execute(
            select(Subject).where(Subject.tenant_id == tenant_id , Subject.name == subject_name )
        )
        return result.scalar_one_or_none()



    
    @staticmethod
    async def get_subject_by_code(db : AsyncSession , tenant_id : UUID , subject_code : str) -> Subject | None:
        result = await db.execute(
            select(Subject).where(Subject.tenant_id == tenant_id , Subject.code == subject_code)
        )
        return result.scalar_one_or_none()




    
    @staticmethod
    async def list_all_subjects(db : AsyncSession , 
      tenant_id : UUID , *, 
      skip : int = 0 , 
      limit : int = 100 ,
      is_active : bool | None = None,
      search : str | None = None

      ) -> tuple[list[Subject], int]:
        filters = [Subject.tenant_id == tenant_id]

        if is_active is not None: #if provided adds is_active to the filter
            filters.append(Subject.is_active == is_active)

        if search: #adds search(subject_name) to the filter if provided
            filters.append(Subject.name.ilike(f"%{search}%"))



        #counts the total number of subjects found by filter
        total_result = await db.execute(
            select(func.count()).select_from(Subject).where(*filters)
        )
        total = total_result.scalar_one()



        result = await db.execute(
            select(Subject)
            .where(*filters)
            .order_by(Subject.name.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all()) , total 
        




    
    @staticmethod
    async def update_subject(db: AsyncSession , subject : Subject , update_data : dict) -> Subject:
        for field , value in update_data.items():
            setattr(subject , field , value)

        await db.flush()
        await db.refresh(subject)
        return subject





    
    @staticmethod
    async def delete_subject(db: AsyncSession , subject : Subject) -> None:
        await db.delete(subject)
        await db.flush()