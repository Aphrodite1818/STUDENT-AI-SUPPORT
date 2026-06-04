#======================================#
#       core/utils/email_templates.py  #
#======================================#

from datetime import datetime

def get_otp_email_html(code: str, purpose: str, expiration_minutes: int) -> str:
    purpose_text = "account verification" if purpose == "verification" else "password reset"
    year = datetime.now().year
    
    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #F4EBD0; margin: 0; padding: 40px 20px; color: #0F172A;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #FFFFFF; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.1), 0 4px 6px -2px rgba(15, 23, 42, 0.05);">
        
        <!-- Header -->
        <div style="background-color: #1E293B; padding: 30px; text-align: center;">
            <h1 style="margin: 0; font-size: 24px; font-weight: 600; color: #FFFFFF; letter-spacing: 0.5px;">LearnlyAi</h1>
        </div>
        
        <!-- Body Content -->
        <div style="padding: 40px 30px;">
            <p style="font-size: 16px; line-height: 1.6; margin: 0 0 20px 0; color: #334155;">Hello,</p>
            <p style="font-size: 16px; line-height: 1.6; margin: 0 0 30px 0; color: #334155;">
                You requested a one-time code for <strong>{purpose_text}</strong>. Please use the verification code below to complete your request:
            </p>
            
            <!-- Verification Code -->
            <div style="text-align: center; margin: 35px 0;">
                <span style="display: inline-block; font-size: 36px; font-weight: 700; letter-spacing: 8px; color: #F59E0B; background-color: #FFF8E1; padding: 20px 40px; border-radius: 8px; border: 2px dashed #F59E0B;">
                    {code}
                </span>
            </div>
            
            <p style="font-size: 15px; line-height: 1.6; margin: 30px 0 0 0; color: #64748B;">
                This code will expire in <strong>{expiration_minutes} minutes</strong>. If you did not request this, you can safely ignore and delete this email.
            </p>
        </div>
        
        <!-- Footer -->
        <div style="background-color: #F8FAFC; padding: 25px 30px; text-align: center; border-top: 1px solid #E2E8F0;">
            <p style="margin: 0; font-size: 14px; color: #64748B;">
                &copy; {year} Tenant Management System. All rights reserved.
            </p>
        </div>
        
    </div>
</body>
</html>
"""
