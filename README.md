# WhatsApp Webhook Review Branch

This branch is a trimmed review snapshot of the WhatsApp AI integration.

It keeps only the files that directly power:

- the FastAPI webhook entrypoint
- Twilio WhatsApp reply sending
- Gemini-backed AI response generation
- the schemas, helpers, and config those flows depend on

## Main Files To Review

- `school_ai_assistant/src/main.py`
- `school_ai_assistant/src/routes/webhook.py`
- `school_ai_assistant/src/services/ai_service.py`
- `school_ai_assistant/src/services/whatsapp_service.py`
- `school_ai_assistant/src/schemas/webhook.py`
- `school_ai_assistant/src/schemas/ai.py`
- `school_ai_assistant/src/helpers/webhook_helper.py`
- `school_ai_assistant/src/helpers/ai_helper.py`
- `school_ai_assistant/src/core/config.py`

## Supporting Files Kept

- package `__init__.py` files
- `school_ai_assistant/src/schemas/common.py`
- `school_ai_assistant/src/helpers/config_helper.py`
- `school_ai_assistant/src/core/exceptions.py`
- `school_ai_assistant/src/core/logging.py`
- dependency manifests at the repo root

Everything else was removed on this branch only to make code review easier.
