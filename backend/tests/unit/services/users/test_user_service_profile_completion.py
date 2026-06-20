from datetime import date
from types import SimpleNamespace
from unittest.mock import ANY, AsyncMock, patch
from uuid import uuid4

import pytest

from app.core.exceptions import BadRequestException
from app.modules.students.models import Gender, StudentProfileStatus
from app.modules.users.models import UserRole
from app.modules.users.service import UserService


def _actor(role: UserRole):
    return SimpleNamespace(
        id=uuid4(),
        tenant_id=uuid4(),
        role=role,
        firstname=None,
        lastname=None,
        phone_number=None,
        whatsapp_id=None,
        profile_completed=False,
    )


def _success_response():
    return SimpleNamespace(profile_completed=True)




@pytest.mark.asyncio
async def test_submit_parent_profile_completion_marks_user_complete():
    actor = _actor(UserRole.PARENT)
    parent = SimpleNamespace(
        id=uuid4(),
        tenant_id=actor.tenant_id,
        user_id=actor.id,
        occupation=None,
        address=None,
        emergency_phone=None,
    )
    payload = {
        "user": {
            "firstname": "Grace",
            "lastname": "Cole",
            "phone_number": "+2348012345678",
            "whatsapp_id": None,
        },
        "role_profile": {
            "occupation": "Engineer",
            "address": "12 Palm Avenue",
            "emergency_phone": "+2348098765432",
        },
    }

    with patch.object(
        UserService,
        "_ensure_parent_profile",
        new=AsyncMock(return_value=parent),
    ), patch(
        "app.modules.users.service.ParentRepository.update_parent",
        new=AsyncMock(return_value=parent),
    ), patch(
        "app.modules.users.service.UserRepository.get_by_phone_number",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.modules.users.service.UserRepository.get_by_whatsapp_id",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.modules.users.service.UserRepository.save_user",
        new=AsyncMock(side_effect=lambda db, user: user),
    ), patch.object(
        UserService,
        "get_profile_completion_schema",
        new=AsyncMock(return_value=_success_response()),
    ):
        response = await UserService.submit_profile_completion(
            db=AsyncMock(),
            actor=actor,
            payload=payload,
        )

    assert response.profile_completed is True
    assert actor.profile_completed is True
    assert parent.occupation == "Engineer"
    assert parent.address == "12 Palm Avenue"
    assert parent.emergency_phone == "+2348098765432"


@pytest.mark.asyncio
async def test_submit_teacher_profile_completion_marks_user_complete():
    actor = _actor(UserRole.TEACHER)
    teacher = SimpleNamespace(
        id=uuid4(),
        tenant_id=actor.tenant_id,
        user_id=actor.id,
        staff_id=None,
        qualification=None,
        specialization=None,
    )
    payload = {
        "user": {
            "firstname": "James",
            "lastname": "Stone",
            "phone_number": "+2348012345678",
            "whatsapp_id": None,
        },
        "role_profile": {
            "staff_id": "T-1001",
            "qualification": "B.Ed",
            "specialization": "Mathematics",
        },
    }

    with patch.object(
        UserService,
        "_get_or_create_teacher_profile",
        new=AsyncMock(return_value=teacher),
    ), patch(
        "app.modules.users.service.TeacherRepository.get_teacher_by_staff_id",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.modules.users.service.UserRepository.get_by_phone_number",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.modules.users.service.UserRepository.get_by_whatsapp_id",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.modules.users.service.TeacherRepository.update_teacher",
        new=AsyncMock(return_value=teacher),
    ), patch(
        "app.modules.users.service.UserRepository.save_user",
        new=AsyncMock(side_effect=lambda db, user: user),
    ), patch.object(
        UserService,
        "get_profile_completion_schema",
        new=AsyncMock(return_value=_success_response()),
    ):
        response = await UserService.submit_profile_completion(
            db=AsyncMock(),
            actor=actor,
            payload=payload,
        )

    assert response.profile_completed is True
    assert actor.profile_completed is True
    assert teacher.staff_id == "T-1001"
    assert teacher.qualification == "B.Ed"
    assert teacher.specialization == "Mathematics"


@pytest.mark.asyncio
async def test_submit_admin_profile_completion_marks_user_complete_and_tenant_complete():
    actor = _actor(UserRole.ADMIN)
    tenant = SimpleNamespace(
        id=actor.tenant_id,
        school_name="NHS School",
        slug="nhs-school",
        email="admin@school.test",
        phone=None,
        address=None,
        city=None,
        state=None,
        country="Nigeria",
        admission_number_prefix=None,
        onboarding_completed=False,
    )
    payload = {
        "user": {
            "firstname": "Taiwo",
            "lastname": "Admin",
            "phone_number": "+2348012345678",
            "whatsapp_id": None,
        },
        "tenant": {
            "school_name": "NHS School",
            "phone": "+2348099999999",
            "address": "42 Unity Road",
            "city": "Lagos",
            "state": "Lagos",
            "country": "Nigeria",
            "admission_number_prefix": "nhs",
        },
    }

    with patch(
        "app.modules.users.service.TenantRepository.get_by_id",
        new=AsyncMock(return_value=tenant),
    ), patch(
        "app.modules.users.service.TenantRepository.get_by_admission_number_prefix",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.modules.users.service.UserRepository.get_by_phone_number",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.modules.users.service.UserRepository.get_by_whatsapp_id",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.modules.users.service.TenantRepository.save",
        new=AsyncMock(return_value=tenant),
    ), patch(
        "app.modules.users.service.UserRepository.save_user",
        new=AsyncMock(side_effect=lambda db, user: user),
    ), patch.object(
        UserService,
        "get_profile_completion_schema",
        new=AsyncMock(return_value=_success_response()),
    ):
        response = await UserService.submit_profile_completion(
            db=AsyncMock(),
            actor=actor,
            payload=payload,
        )

    assert response.profile_completed is True
    assert actor.profile_completed is True
    assert tenant.phone == "+2348099999999"
    assert tenant.admission_number_prefix == "NHS"
    assert tenant.onboarding_completed is True


@pytest.mark.asyncio
async def test_resubmitting_parent_profile_completion_updates_existing_profile_without_duplication():
    actor = _actor(UserRole.PARENT)
    actor.profile_completed = True
    parent = SimpleNamespace(
        id=uuid4(),
        tenant_id=actor.tenant_id,
        user_id=actor.id,
        occupation="Teacher",
        address="Old address",
        emergency_phone=None,
    )
    payload = {
        "user": {
            "firstname": "Grace",
            "lastname": "Cole",
            "phone_number": "+2348012345678",
            "whatsapp_id": None,
        },
        "role_profile": {
            "occupation": "Doctor",
            "address": "New address",
            "emergency_phone": "+2348098765432",
        },
    }

    with patch.object(
        UserService,
        "_ensure_parent_profile",
        new=AsyncMock(return_value=parent),
    ) as ensure_parent_profile, patch(
        "app.modules.users.service.ParentRepository.update_parent",
        new=AsyncMock(return_value=parent),
    ) as update_parent, patch(
        "app.modules.users.service.UserRepository.get_by_phone_number",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.modules.users.service.UserRepository.get_by_whatsapp_id",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.modules.users.service.UserRepository.save_user",
        new=AsyncMock(side_effect=lambda db, user: user),
    ), patch.object(
        UserService,
        "get_profile_completion_schema",
        new=AsyncMock(return_value=_success_response()),
    ):
        await UserService.submit_profile_completion(
            db=AsyncMock(),
            actor=actor,
            payload=payload,
        )

    assert parent.occupation == "Doctor"
    assert parent.address == "New address"
    ensure_parent_profile.assert_awaited_once()
    update_parent.assert_awaited_once()


@pytest.mark.asyncio
async def test_wrong_role_payload_fails_cleanly():
    actor = _actor(UserRole.PARENT)
    payload = {
        "user": {
            "firstname": "Ada",
            "lastname": "Cole",
            "phone_number": "+2348012345678",
            "whatsapp_id": None,
        },
        "tenant": {
            "school_name": "Should not be here",
            "admission_number_prefix": "NHS",
        },
    }

    with pytest.raises(BadRequestException) as exc_info:
        await UserService.submit_profile_completion(
            db=AsyncMock(),
            actor=actor,
            payload=payload,
        )

    assert isinstance(exc_info.value.detail, list)
    assert any(error["loc"][-1] == "role_profile" for error in exc_info.value.detail)
