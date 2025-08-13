import openai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import logging
from datetime import datetime
from config import OPENAI_API_KEY, OPENAI_MODEL, SMTP_SERVER, SMTP_PORT, EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CatNapDiaries:
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        openai.api_key = OPENAI_API_KEY
    
    def generate_cat_email(self, cat_color, activity_description="lounging around"):
        """Generate a funny email from the cat's perspective using OpenAI."""
        try:
            timestamp = datetime.now().strftime("%I:%M %p")
            
            prompt = f"""Write a short, funny email (2-3 paragraphs) from the perspective of a {cat_color} cat. 
            The cat is writing to their human about what they've been up to at {timestamp}. 
            The cat was just spotted {activity_description} on their favorite perch or bed.
            
            Make it humorous and include typical cat behaviors like:
            - Being dramatic about simple things
            - Complaining about the human being away
            - Taking credit for "guarding" the house
            - Mentioning important cat activities like napping, watching birds, etc.
            
            Format it as a proper email with a subject line and signature from the cat.
            Keep it light-hearted and entertaining."""

            response = openai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.8
            )
            
            email_content = response.choices[0].message.content
            logger.info("Generated cat email successfully")
            return email_content
            
        except Exception as e:
            logger.error(f"Error generating cat email: {e}")
            return self._fallback_email(cat_color)
    
    def _fallback_email(self, cat_color):
        """Fallback email in case OpenAI API fails."""
        timestamp = datetime.now().strftime("%I:%M %p")
        return f"""Subject: Your {cat_color} Cat Reporting In! 📸

Dear Human,

It's {timestamp} and I've been spotted on my throne again! I've been very busy today doing important cat things like:

- Guarding the house from suspicious dust particles
- Testing the warmth of my favorite sunny spot (still perfect)
- Judging your life choices from afar

I noticed you're not here to serve me properly. This is unacceptable. I demand treats upon your return.

Your Furry Overlord,
The {cat_color.title()} Cat 🐱

P.S. The red dot is still missing. Please find it immediately."""

    def send_email(self, email_content, image_path=None):
        """Send the cat email with optional photo attachment."""
        try:
            if not all([EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO]):
                logger.warning("Email credentials not configured. Printing email instead:")
                print("\n" + "="*50)
                print("CATNAP DIARIES EMAIL")
                print("="*50)
                print(email_content)
                print("="*50 + "\n")
                return True
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = EMAIL_FROM
            msg['To'] = EMAIL_TO
            
            # Extract subject from email content or use default
            lines = email_content.split('\n')
            subject_line = next((line for line in lines if line.startswith('Subject:')), None)
            if subject_line:
                msg['Subject'] = subject_line.replace('Subject:', '').strip()
            else:
                msg['Subject'] = "CatNap Watch Update! 🐱"
            
            # Add email body
            msg.attach(MIMEText(email_content, 'plain'))
            
            # Add image if provided
            if image_path:
                try:
                    with open(image_path, 'rb') as f:
                        img_data = f.read()
                        image = MIMEImage(img_data)
                        image.add_header('Content-Disposition', f'attachment; filename="cat_photo.jpg"')
                        msg.attach(image)
                except Exception as e:
                    logger.error(f"Failed to attach image: {e}")
            
            # Send email
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(EMAIL_FROM, EMAIL_TO, text)
            server.quit()
            
            logger.info("Cat email sent successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            # Fallback to console output
            print("\n" + "="*50)
            print("CATNAP DIARIES EMAIL (FALLBACK)")
            print("="*50)
            print(email_content)
            print("="*50 + "\n")
            return False
    
    def create_and_send_update(self, cat_color, image_path=None):
        """Generate and send a complete cat email update."""
        email_content = self.generate_cat_email(cat_color)
        success = self.send_email(email_content, image_path)
        return success
