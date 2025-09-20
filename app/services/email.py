from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.config import settings
from typing import List

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="Contact Management API",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_verification_email(email: str, token: str):
    """Відправка email для верифікації"""
    verification_url = f"http://localhost:8000/api/v1/auth/verify-email?token={token}"
    
    message = MessageSchema(
        subject="Verify your email - Contact Management API",
        recipients=[email],
        body=f"""
        <html>
            <body>
                <h2>Welcome to Contact Management API!</h2>
                <p>Thank you for registering. Please click the link below to verify your email address:</p>
                <p><a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a></p>
                <p>Or copy and paste this link in your browser:</p>
                <p>{verification_url}</p>
                <p>If you didn't create this account, please ignore this email.</p>
                <br>
                <p>Best regards,<br>Contact Management API Team</p>
            </body>
        </html>
        """,
        subtype="html"
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)