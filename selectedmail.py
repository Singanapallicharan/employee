import os
import django
from django.template.loader import render_to_string

from weasyprint import HTML
from io import BytesIO

import weasyprint

# Set Django settings
print(weasyprint.__version__)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eligodb.settings")
django.setup()

from db.models import Employee
from django.core.mail import EmailMessage

def generate_combined_pdf(employee):
    # Render each template with context
    context = {"employee": employee}
    html1 = render_to_string("template1.html", context)
    html2 = render_to_string("template2.html", context)

    # Combine both HTMLs
    full_html = html1 + '<p style="page-break-after: always;"></p>' + html2

    # Convert to PDF
    pdf_file = BytesIO()
    HTML(string=full_html).write_pdf(pdf_file)
    pdf_file.seek(0)
    return pdf_file

def send_offer_letters():
    selected_employees = Employee.objects.filter(status='Selected',)
    print(selected_employees)

    for emp in selected_employees:
        print(emp.first_name)
        if emp.first_name == "Charan":
            pdf = generate_combined_pdf(emp)

            full_name = f"{emp.first_name} {emp.last_name}".strip()
            email = EmailMessage(
                subject="🎉 You're Selected at EliGo!",
                body=f"Hi {full_name},\n\nCongratulations! Please find your offer letter attached.",
                from_email="careers@eligo.space",
                to=[emp.email],
            )

            email.attach(f"OfferLetter_{full_name.replace(' ', '_')}.pdf", pdf.read(), 'application/pdf')

            try:
                email.send()
                emp.save()
                print(f"✅ Sent to {emp.email}")
            except Exception as e:
                print(f"❌ Failed for {emp.email}: {e}")

if __name__ == "__main__":
    send_offer_letters()
