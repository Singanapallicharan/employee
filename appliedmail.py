import os
import django

# Set the settings module for Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eligodb.settings")
django.setup()

from django.core.mail import EmailMessage
from db.models import Employee

def send_application_acknowledgments():
    print("Script started")
    applicants = Employee.objects.filter(status='Applied')
    print(applicants)

    for app in applicants:
        full_name = f"{app.first_name or ''} {app.last_name or ''}".strip() or "Applicant"
        html_body = create_email_body(full_name)

        email = EmailMessage(
            subject="✅ Your Application to EliGo Has Been Received",
            body=html_body,
            from_email="careers@eligo.space",
            to=[app.email],
        )
        email.content_subtype = "html"  # Required to send HTML emails

        try:
            email.send()
            app.email_sent = True
            app.save()
        except Exception as e:
            print(f"Failed to send email to {app.email}: {e}")

def create_email_body(full_name: str) -> str:
    company_name = "EliGo"
    company_email = "careers@eligo.space"
    company_website = "https://www.eligo.space"

    return f"""
    <div style="font-family: Arial, sans-serif; color: #333; padding: 20px; max-width: 600px; margin: auto;">
      <h2 style="color: #008080;">Thank you for applying to {company_name}!</h2>
      
      <p>Dear <strong>{full_name}</strong>,</p>
      
      <p>We are thrilled to inform you that <strong>your application has been successfully registered</strong>.</p>
      
      <p>
        Our team will carefully review your details. If your profile matches the requirements,
        you'll hear from us shortly with the next steps.
      </p>

      <p>
        In the meantime, feel free to explore our work and culture at 
        <a href="{company_website}" target="_blank">{company_website}</a>.
      </p>

      <p>
        If you have any questions, you can reply to this email or contact us at 
        <a href="mailto:{company_email}">{company_email}</a>.
      </p>

      <br/>
      <p>Warm regards,<br><strong>The {company_name} Team</strong></p>
      <hr style="border: none; border-top: 1px solid #ddd;" />
      <p style="font-size: 12px; text-align: center; color: #999;">
        {company_name} | Building India's Future Interns | Bengaluru, India
      </p>
    </div>
    """

if __name__ == "__main__":
    send_application_acknowledgments()

