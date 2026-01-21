import aiosmtplib

import logging

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings


logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.email_from = settings.EMAIL_FROM

    async def send_verification_email(self, email: str, code: str) -> bool:
        try:
            message = MIMEMultipart("alternative")
            message["From"] = self.email_from
            message["To"] = email
            message["Subject"] = "Код подтверждения регистрации"

            text = f"""
            Код подтверждения: {code}
            
            Введите этот код в приложении для подтверждения регистрации.
            Код действителен 15 минут.
            
            Если вы не регистрировались, проигнорируйте это письмо.
            """
            message.attach(MIMEText(text, "plain", "utf-8"))

            html = f"""
            <!DOCTYPE html>
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Код подтверждения: <strong>{code}</strong></h2>
                    <p>Введите этот код в приложении для подтверждения регистрации.</p>
                    <p><em>Код действителен 15 минут.</em></p>
                    <hr>
                    <p style="color: #666; font-size: 12px;">
                    Если вы не регистрировались, проигнорируйте это письмо.
                    </p>
                </body>
            </html>
            """

            message.attach(MIMEText(html, "html", "utf-8"))

            async with aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=False,
                start_tls=True,
            ) as smtp:
                logger.info("Подключено, логинюсь")
                await smtp.login(self.smtp_user, self.smtp_password)
                logger.info("Логин успешен, отправляю")
                await smtp.send_message(message)
                logger.info(f"Email успешно отправлен на {email}")
                return True

        except aiosmtplib.SMTPAuthenticationError as e:
            logger.error(f"Ошибка аутентификации SMTP: {e}")
            logger.error("Проверь логин/пароль и включена ли 2FA в Яндексе")
            return False
        except aiosmtplib.SMTPException as e:
            logger.error(f"Ошибка SMTP: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {type(e).__name__}: {e}")
            return False
