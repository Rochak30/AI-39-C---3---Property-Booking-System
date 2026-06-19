"""
Email Service — sends password reset codes and booking confirmations via Gmail SMTP.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config


def send_reset_code(to_email: str, code: str) -> bool:
    """Send a 6-digit reset code. Returns True on success."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"{code} is your Pahuna reset code"
        msg["From"]    = config.GMAIL_ADDRESS
        msg["To"]      = to_email

        plain = f"""
Hi,

Your Pahuna password reset code is:

  {code}

This code expires in 10 minutes. If you didn't request this, ignore this email.

— The Pahuna Team
        """.strip()

        html = f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#0d1117;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0d1117;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="480" cellpadding="0" cellspacing="0"
               style="background:#161b22;border-radius:16px;border:1px solid #21262d;overflow:hidden;">
          <tr>
            <td style="background:linear-gradient(135deg,#0d1f3c,#1a3a5c,#0d2a2a);padding:32px;text-align:center;">
              <div style="font-size:28px;font-weight:800;color:#ffffff;letter-spacing:-0.5px;">Pahuna</div>
              <div style="font-size:13px;color:#8b949e;margin-top:4px;">Nepal's trusted accommodation platform</div>
            </td>
          </tr>
          <tr>
            <td style="padding:36px 40px;">
              <p style="margin:0 0 8px;font-size:15px;color:#8b949e;">Hi there,</p>
              <p style="margin:0 0 28px;font-size:15px;color:#c9d1d9;line-height:1.6;">
                We received a request to reset your Pahuna password. Use the code below:
              </p>
              <div style="background:#0d1117;border:1.5px solid #00c97a;border-radius:12px;
                          padding:24px;text-align:center;margin-bottom:28px;">
                <div style="font-size:42px;font-weight:800;letter-spacing:10px;
                            color:#00c97a;font-family:'Courier New',monospace;">{code}</div>
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
          <tr>
            <td style="padding:20px 40px;border-top:1px solid #21262d;text-align:center;">
              <p style="margin:0;font-size:12px;color:#484f58;">© 2026 Pahuna · Nepal's Homestay Booking Platform</p>
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
        print(f"EMAIL SEND ERROR (reset): {e}")
        return False


def send_booking_confirmation(
    guest_email: str,
    guest_name: str,
    property_title: str,
    checkin_date: str,
    checkout_date: str,
    total_amount: float,
    booking_ref: str,
) -> bool:
    """
    Send a confirmation email to the guest after their booking is confirmed by the host.
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Booking Confirmed – {property_title} – Pahuna"
        msg["From"]    = config.GMAIL_ADDRESS
        msg["To"]      = guest_email

        plain = f"""
Hi {guest_name},

Great news! Your booking at {property_title} has been confirmed by the host.

Booking reference: {booking_ref}
Check-in:  {checkin_date}
Check-out: {checkout_date}
Total paid: NPR {total_amount:,.2f}

You can view your booking details in your Pahuna dashboard.

Need help? Contact us at support@pahuna.com

— The Pahuna Team
        """.strip()

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
              <div style="font-size:28px;font-weight:800;color:#ffffff;letter-spacing:-0.5px;">Pahuna</div>
              <div style="font-size:13px;color:#8b949e;margin-top:4px;">Nepal's trusted accommodation platform</div>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:36px 40px;">
              <p style="margin:0 0 8px;font-size:15px;color:#8b949e;">Hi {guest_name},</p>
              <p style="margin:0 0 28px;font-size:15px;color:#c9d1d9;line-height:1.6;">
                Great news! Your booking at <strong style="color:#00c97a;">{property_title}</strong>
                has been confirmed by the host.
              </p>

              <!-- Booking details -->
              <div style="background:#0d1117;border:1px solid #30363d;border-radius:12px;padding:20px;margin-bottom:28px;">
                <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px dashed #21262d;">
                  <span style="color:#8b949e;">Reference</span>
                  <span style="color:#ffffff;font-weight:600;">{booking_ref}</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px dashed #21262d;">
                  <span style="color:#8b949e;">Check-in</span>
                  <span style="color:#ffffff;font-weight:600;">{checkin_date}</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px dashed #21262d;">
                  <span style="color:#8b949e;">Check-out</span>
                  <span style="color:#ffffff;font-weight:600;">{checkout_date}</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:8px 0;">
                  <span style="color:#8b949e;">Total Paid</span>
                  <span style="color:#00c97a;font-weight:700;">NPR {total_amount:,.2f}</span>
                </div>
              </div>

              <p style="margin:0 0 8px;font-size:13px;color:#8b949e;line-height:1.6;">
                You can view your booking details in your
                <a href="#" style="color:#00c97a;text-decoration:none;">Pahuna dashboard</a>.
                If you have any questions, feel free to reply to this email or contact the host directly
                through the platform.
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
            server.sendmail(config.GMAIL_ADDRESS, guest_email, msg.as_bytes())

        print(f"Booking confirmation sent to {guest_email} for booking {booking_ref}")
        return True

    except Exception as e:
        print(f"EMAIL SEND ERROR (booking confirmation): {e}")
        return False
def send_property_approval_email(host_email, host_name, property_title):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"✅ Your property '{property_title}' has been approved!"
        msg["From"] = config.GMAIL_ADDRESS
        msg["To"] = host_email

        plain = f"""
Hi {host_name},

Great news! Your property "{property_title}" has been approved by our team.

Please note: It will take up to 1 week for your property to appear on the browse page as we finalize the listing details.

Thank you for choosing Pahuna.

— The Pahuna Team
        """.strip()

        html = f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#0d1117;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0d1117;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="480" cellpadding="0" cellspacing="0"
               style="background:#161b22;border-radius:16px;border:1px solid #21262d;overflow:hidden;">
          <tr>
            <td style="background:linear-gradient(135deg,#0d1f3c,#1a3a5c,#0d2a2a);padding:32px;text-align:center;">
              <div style="font-size:28px;font-weight:800;color:#ffffff;letter-spacing:-0.5px;">Pahuna</div>
              <div style="font-size:13px;color:#8b949e;margin-top:4px;">Nepal's trusted accommodation platform</div>
            </td>
          </tr>
          <tr>
            <td style="padding:36px 40px;">
              <p style="margin:0 0 8px;font-size:15px;color:#8b949e;">Hi {host_name},</p>
              <p style="margin:0 0 28px;font-size:15px;color:#c9d1d9;line-height:1.6;">
                Great news! Your property "<strong style="color:#00c97a;">{property_title}</strong>" has been approved by our team.
              </p>
              <div style="background:#0d1117;border:1px solid #30363d;border-radius:12px;padding:20px;margin-bottom:28px;">
                <p style="margin:0;font-size:14px;color:#8b949e;">
                  Please note: It will take <strong style="color:#f0a500;">up to 1 week</strong> for your property to appear on the browse page as we finalize the listing details.
                </p>
              </div>
              <p style="margin:0 0 8px;font-size:13px;color:#8b949e;line-height:1.6;">
                Thank you for choosing Pahuna. We look forward to hosting your guests!
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding:20px 40px;border-top:1px solid #21262d;text-align:center;">
              <p style="margin:0;font-size:12px;color:#484f58;">© 2026 Pahuna · Nepal's Homestay Booking Platform</p>
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
            server.sendmail(config.GMAIL_ADDRESS, host_email, msg.as_bytes())

        print(f"Property approval email sent to {host_email}")
        return True
    except Exception as e:
        print(f"EMAIL SEND ERROR (property approval): {e}")
        return False

def send_property_rejection_email(host_email, host_name, property_title):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"❌ Your property '{property_title}' was not approved"
        msg["From"] = config.GMAIL_ADDRESS
        msg["To"] = host_email

        plain = f"""
Hi {host_name},

We regret to inform you that your property "{property_title}" was not approved for listing at this time.

Please review our guidelines and you may resubmit with updated details.

— The Pahuna Team
        """.strip()

        html = f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#0d1117;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0d1117;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="480" cellpadding="0" cellspacing="0"
               style="background:#161b22;border-radius:16px;border:1px solid #21262d;overflow:hidden;">
          <tr>
            <td style="background:linear-gradient(135deg,#0d1f3c,#1a3a5c,#0d2a2a);padding:32px;text-align:center;">
              <div style="font-size:28px;font-weight:800;color:#ffffff;letter-spacing:-0.5px;">Pahuna</div>
              <div style="font-size:13px;color:#8b949e;margin-top:4px;">Nepal's trusted accommodation platform</div>
            </td>
          </tr>
          <tr>
            <td style="padding:36px 40px;">
              <p style="margin:0 0 8px;font-size:15px;color:#8b949e;">Hi {host_name},</p>
              <p style="margin:0 0 28px;font-size:15px;color:#c9d1d9;line-height:1.6;">
                We regret to inform you that your property "<strong style="color:#e74c3c;">{property_title}</strong>" was not approved for listing at this time.
              </p>
              <div style="background:#0d1117;border:1px solid #30363d;border-radius:12px;padding:20px;margin-bottom:28px;">
                <p style="margin:0;font-size:14px;color:#8b949e;">
                  Please review our listing guidelines and you may resubmit your property with updated details.
                </p>
              </div>
              <p style="margin:0 0 8px;font-size:13px;color:#8b949e;line-height:1.6;">
                If you have any questions, please contact us.
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding:20px 40px;border-top:1px solid #21262d;text-align:center;">
              <p style="margin:0;font-size:12px;color:#484f58;">© 2026 Pahuna · Nepal's Homestay Booking Platform</p>
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
            server.sendmail(config.GMAIL_ADDRESS, host_email, msg.as_bytes())

        print(f"Property rejection email sent to {host_email}")
        return True
    except Exception as e:
        print(f"EMAIL SEND ERROR (property rejection): {e}")
        return False    