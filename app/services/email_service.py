"""
Email Service — sends password reset codes via Gmail SMTP.

Setup (one-time):
  1. Go to myaccount.google.com → Security → 2-Step Verification → turn ON
  2. Go to myaccount.google.com → Security → App Passwords
  3. Create an app password (name it "Pahuna")
  4. Copy the 16-character password into config.py as GMAIL_APP_PASSWORD
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config


def send_reset_code(to_email: str, code: str) -> bool:
    """
    Send a 6-digit reset code to the given email.
    Returns True on success, False on failure.
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"{code} is your Pahuna reset code"
        msg["From"]    = config.GMAIL_ADDRESS
        msg["To"]      = to_email

        # Plain text fallback
        plain = f"""
Hi,

Your Pahuna password reset code is:

  {code}

This code expires in 10 minutes. If you didn't request this, ignore this email.

— The Pahuna Team
        """.strip()

        # HTML version
        html = f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#0d1117;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0d1117;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="480" cellpadding="0" cellspacing="0"
               style="background:#161b22;border-radius:16px;border:1px solid #21262d;overflow:hidden;">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#0d1f3c,#1a3a5c,#0d2a2a);padding:32px;text-align:center;">
              <div style="font-size:28px;font-weight:800;color:#ffffff;letter-spacing:-0.5px;">
                Pahuna
              </div>
              <div style="font-size:13px;color:#8b949e;margin-top:4px;">Nepal's trusted accommodation platform</div>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:36px 40px;">
              <p style="margin:0 0 8px;font-size:15px;color:#8b949e;">Hi there,</p>
              <p style="margin:0 0 28px;font-size:15px;color:#c9d1d9;line-height:1.6;">
                We received a request to reset your Pahuna password. Use the code below:
              </p>

              <!-- Code block -->
              <div style="background:#0d1117;border:1.5px solid #00c97a;border-radius:12px;
                          padding:24px;text-align:center;margin-bottom:28px;">
                <div style="font-size:42px;font-weight:800;letter-spacing:10px;
                            color:#00c97a;font-family:'Courier New',monospace;">
                  {code}
                </div>
                <div style="font-size:12px;color:#8b949e;margin-top:8px;">
                  Expires in <strong style="color:#f0a500;">10 minutes</strong>
                </div>
              </div>

              <p style="margin:0 0 8px;font-size:13px;color:#8b949e;line-height:1.6;">
                Enter this code on the verification page. If you didn't request a password reset,
                you can safely ignore this email — your account is secure.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:20px 40px;border-top:1px solid #21262d;text-align:center;">
              <p style="margin:0;font-size:12px;color:#484f58;">
                © 2026 Pahuna · Nepal's Homestay Booking Platform
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
        """

        msg.attach(MIMEText(plain, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(config.GMAIL_ADDRESS, config.GMAIL_APP_PASSWORD)
            server.sendmail(config.GMAIL_ADDRESS, to_email, msg.as_bytes())

        print(f"Reset code sent to {to_email}")
        return True

    except Exception as e:
        print(f"EMAIL SEND ERROR: {e}")
        return False