import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
from datetime import datetime, timedelta

class EmailService:
    # Almacenamiento temporal de códigos (en producción usa Redis o DB)
    verification_codes = {}
    
    @staticmethod
    def generate_verification_code(length=6):
        """Generar código de verificación aleatorio"""
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def send_verification_email(user_email, user_name, verification_code):
        """Enviar email de verificación"""
        try:
            print(f"📧 Preparando envío de email de verificación a: {user_email}")
            
            # Configuración del servidor SMTP de Gmail
            smtp_server = "smtp.gmail.com"
            port = 587
            sender_email = os.getenv('GMAIL_EMAIL')
            sender_password = os.getenv('GMAIL_APP_PASSWORD')
            
            if not sender_email or not sender_password:
                raise ValueError("Configuración de email no encontrada en variables de entorno")
            
            # Crear el mensaje
            message = MIMEMultipart("alternative")
            message["Subject"] = "Verifica tu cuenta - Liga Ágil"
            message["From"] = sender_email
            message["To"] = user_email
            
            # Crear el contenido del email
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #2563eb; color: white; padding: 20px; text-align: center; }}
                    .code {{ font-size: 32px; font-weight: bold; color: #2563eb; text-align: center; margin: 20px 0; }}
                    .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Liga Ágil</h1>
                    </div>
                    
                    <h2>Hola {user_name},</h2>
                    
                    <p>Gracias por registrarte en Liga Ágil. Para completar tu registro, por favor utiliza el siguiente código de verificación:</p>
                    
                    <div class="code">{verification_code}</div>
                    
                    <p>Este código expirará en 15 minutos.</p>
                    
                    <p>Si no solicitaste este registro, por favor ignora este email.</p>
                    
                    <div class="footer">
                        <p>© 2024 Liga Ágil. Todos los derechos reservados.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Versión texto plano
            text_content = f"""
            Hola {user_name},
            
            Gracias por registrarte en Liga Ágil.
            
            Tu código de verificación es: {verification_code}
            
            Este código expirará en 15 minutos.
            
            Si no solicitaste este registro, por favor ignora este email.
            
            Saludos,
            Equipo Liga Ágil
            """
            
            # Convertir a MIMEText objects
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            
            # Agregar partes al mensaje
            message.attach(part1)
            message.attach(part2)
            
            # Enviar email
            print("🔗 Conectando al servidor SMTP...")
            server = smtplib.SMTP(smtp_server, port)
            server.starttls()  # Seguridad
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, user_email, message.as_string())
            server.quit()
            
            print(f"✅ Email de verificación enviado exitosamente a: {user_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error al enviar email de verificación: {str(e)}")
            return False
    
    @staticmethod
    def store_verification_code(email, code):
        """Almacenar código de verificación con timestamp"""
        expiration_time = datetime.now() + timedelta(minutes=15)
        EmailService.verification_codes[email] = {
            'code': code,
            'expires_at': expiration_time,
            'verified': False
        }
        print(f"💾 Código almacenado para {email}: {code} (expira: {expiration_time})")
    
    @staticmethod
    def verify_code(email, code):
        """Verificar código de verificación"""
        print(f"🔍 Verificando código para: {email}")
        
        if email not in EmailService.verification_codes:
            print("❌ No se encontró código para este email")
            return False
        
        stored_data = EmailService.verification_codes[email]
        
        # Verificar expiración
        if datetime.now() > stored_data['expires_at']:
            print("❌ Código expirado")
            del EmailService.verification_codes[email]
            return False
        
        # Verificar código
        if stored_data['code'] == code:
            print("✅ Código verificado correctamente")
            EmailService.verification_codes[email]['verified'] = True
            return True
        
        print("❌ Código incorrecto")
        return False
    
    @staticmethod
    def is_email_verified(email):
        """Verificar si el email ya fue verificado"""
        return (email in EmailService.verification_codes and 
                EmailService.verification_codes[email]['verified'])
    
    @staticmethod
    def cleanup_expired_codes():
        """Limpiar códigos expirados (ejecutar periódicamente)"""
        current_time = datetime.now()
        expired_emails = [
            email for email, data in EmailService.verification_codes.items()
            if current_time > data['expires_at']
        ]
        
        for email in expired_emails:
            del EmailService.verification_codes[email]
            print(f"🗑️ Código expirado eliminado para: {email}")