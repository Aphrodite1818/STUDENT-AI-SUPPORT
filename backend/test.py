

from app.core.utils.email import send_email 
from app.core.utils.email_templates import get_otp_email_html
import asyncio
import time

body = get_otp_email_html("123456","verification",15)
start = time.time()
asyncio.run(send_email("taiwoayimora623@gmail.com" , "unknown" , body , True))
end = time.time()
total = end - start
print(f"completed in {total}")