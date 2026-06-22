# ====================================== #
#       auth_identity/service.py         #
# ====================================== #

"""Auth identity service layer."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.modules.auth_identity.models import ActorType, AuthIdentity, IdentifierType
from app.modules.auth_identity.repository import AuthIdentityRepository
from app.modules.auth_identity.schemas import (
    AuthIdentityCreate,
    AuthIdentityResponse,
    IdentityResolution,
)


class AuthIdentityService:
    """Business logic for creating and resolving login identities."""

    @staticmethod
    def _normalize_identifier(
        identifier: str,
        identifier_type: IdentifierType,
    ) -> str:
        """Normalize login identifier before storing or querying."""

        cleaned_identifier = identifier.strip()

        if identifier_type == IdentifierType.EMAIL:
            return cleaned_identifier.lower()

        if identifier_type == IdentifierType.ADMISSION_NUMBER:
            return cleaned_identifier.upper()

        return cleaned_identifier

    @staticmethod
    async def ensure_identifier_available(
        db: AsyncSession,
        *,
        identifier: str,
        identifier_type: IdentifierType,
        exclude_identity_id: uuid.UUID | None = None,
    ) -> None:
        """Ensure a login identifier is not already assigned to another actor."""

        normalized_identifier = AuthIdentityService._normalize_identifier(
            identifier=identifier,
            identifier_type=identifier_type,
        )

        exists = await AuthIdentityRepository.identifier_exists(
            db=db,
            identifier=normalized_identifier,
            identifier_type=identifier_type,
            exclude_identity_id=exclude_identity_id,
        )

        if exists:
            raise ConflictException("This login identifier is already in use.")

    @staticmethod
    async def create_for_actor(
        db: AsyncSession,
        *,
        tenant_id: uuid.UUID,
        payload: AuthIdentityCreate,
    ) -> AuthIdentityResponse:
        """Create a login identity for an actor."""

        normalized_identifier = AuthIdentityService._normalize_identifier(
            identifier=payload.identifier,
            identifier_type=payload.identifier_type,
        )

        await AuthIdentityService.ensure_identifier_available(
            db=db,
            identifier=normalized_identifier,
            identifier_type=payload.identifier_type,
        )

        existing_actor_identity = await AuthIdentityRepository.get_by_actor(
            db=db,
            actor_type=payload.actor_type,
            actor_id=payload.actor_id,
        )

        if existing_actor_identity is not None:
            raise ConflictException("This actor already has a login identity.")

        identity = AuthIdentity(
            tenant_id=tenant_id,
            identifier=normalized_identifier,
            identifier_type=payload.identifier_type,
            actor_type=payload.actor_type,
            actor_id=payload.actor_id,
            is_active=payload.is_active,
        )

        created_identity = await AuthIdentityRepository.create(
            db=db,
            record=identity,
        )

        return AuthIdentityResponse.model_validate(created_identity)

    @staticmethod
    async def resolve_identifier(
        db: AsyncSession,
        *,
        identifier: str,
        identifier_type: IdentifierType,
    ) -> IdentityResolution:
        """Resolve a login identifier to actor type, actor ID, and tenant ID."""

        normalized_identifier = AuthIdentityService._normalize_identifier(
            identifier=identifier,
            identifier_type=identifier_type,
        )

        identity = await AuthIdentityRepository.get_active_by_identifier(
            db=db,
            identifier=normalized_identifier,
            identifier_type=identifier_type,
        )

        if identity is None:
            raise NotFoundException("Login identity not found.")

        return IdentityResolution(
            actor_type=identity.actor_type,
            actor_id=identity.actor_id,
            tenant_id=identity.tenant_id,
        )

    @staticmethod
    async def update_identifier(
        db: AsyncSession,
        *,
        actor_type: ActorType,
        actor_id: uuid.UUID,
        new_identifier: str,
        identifier_type: IdentifierType,
    ) -> AuthIdentityResponse:
        """Update the login identifier attached to an actor."""

        identity = await AuthIdentityRepository.get_by_actor(
            db=db,
            actor_type=actor_type,
            actor_id=actor_id,
        )

        if identity is None:
            raise NotFoundException("Login identity not found.")

        normalized_identifier = AuthIdentityService._normalize_identifier(
            identifier=new_identifier,
            identifier_type=identifier_type,
        )

        await AuthIdentityService.ensure_identifier_available(
            db=db,
            identifier=normalized_identifier,
            identifier_type=identifier_type,
            exclude_identity_id=identity.id,
        )

        identity.identifier = normalized_identifier
        identity.identifier_type = identifier_type

        updated_identity = await AuthIdentityRepository.save(
            db=db,
            record=identity,
        )

        return AuthIdentityResponse.model_validate(updated_identity)

    @staticmethod
    async def deactivate_for_actor(
        db: AsyncSession,
        *,
        actor_type: ActorType,
        actor_id: uuid.UUID,
    ) -> AuthIdentityResponse:
        """Deactivate an actor login identity."""

        identity = await AuthIdentityRepository.get_by_actor(
            db=db,
            actor_type=actor_type,
            actor_id=actor_id,
        )

        if identity is None:
            raise NotFoundException("Login identity not found.")

        deactivated_identity = await AuthIdentityRepository.deactivate(db, identity)

        return AuthIdentityResponse.model_validate(deactivated_identity)

    @staticmethod
    async def get_identity_for_actor(
        db: AsyncSession,
        *,
        actor_type: ActorType,
        actor_id: uuid.UUID,
    ) -> AuthIdentityResponse:
        """Return the login identity attached to an actor."""

        identity = await AuthIdentityRepository.get_by_actor(
            db=db,
            actor_type=actor_type,
            actor_id=actor_id,
        )

        if identity is None:
            raise NotFoundException("Login identity not found.")

        return AuthIdentityResponse.model_validate(identity)


"""NB: This service does not commit."""