import smtplib
from email.message import EmailMessage
from html import escape

from core.config import settings


def _send_email(
    to_email: str,
    subject: str,
    html_body: str,
) -> bool:
    """
    Send an HTML email using SMTP.
    """

    try:
        message = EmailMessage()

        message["From"] = settings.FROM_EMAIL
        message["To"] = to_email
        message["Subject"] = subject

        # Plain-text fallback
        message.set_content(
            "Doctor Finder notification. "
            "Please open this email in an HTML-compatible email client."
        )

        # HTML version
        message.add_alternative(html_body, subtype="html")

        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            timeout=30,
        ) as server:

            server.starttls()

            server.login(
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD,
            )

            server.send_message(message)

        return True

    except Exception as e:
        print(f"[SMTP] Failed to send email to {to_email}: {e}")
        return False


def send_otp_email(
    to_email: str,
    otp: str,
    first_name: str,
    last_name: str,
) -> bool:
    """
    Send OTP email for password reset.
    """

    full_name = escape(f"{first_name} {last_name}")

    html_body = f"""
    <div style="
        font-family: Arial, sans-serif;
        max-width: 480px;
        margin: 40px auto;
        background: #ffffff;
    ">

        <div style="
            background: #1565C0;
            padding: 28px;
            border-radius: 12px 12px 0 0;
            text-align: center;
        ">
            <h1 style="
                color: #ffffff;
                margin: 0;
                font-size: 28px;
            ">
                Doctor Finder
            </h1>

            <p style="
                color: #BBDEFB;
                margin: 8px 0 0;
                font-size: 15px;
            ">
                Password Reset
            </p>
        </div>

        <div style="
            background: #f5f7fa;
            padding: 32px;
            border-radius: 0 0 12px 12px;
        ">

            <p style="
                color: #333;
                font-size: 16px;
            ">
                Hi <strong>{full_name}</strong>,
            </p>

            <p style="
                color: #555;
                font-size: 15px;
                line-height: 1.6;
            ">
                We received a request to reset your Doctor Finder
                account password.
            </p>

            <p style="
                color: #555;
                font-size: 15px;
                line-height: 1.6;
            ">
                Use the verification code below to continue:
            </p>

            <div style="
                background: #ffffff;
                border: 2px dashed #1565C0;
                border-radius: 12px;
                text-align: center;
                padding: 24px;
                margin: 24px 0;
            ">
                <span style="
                    font-size: 40px;
                    letter-spacing: 12px;
                    font-weight: bold;
                    color: #1565C0;
                    font-family: monospace;
                ">
                    {escape(otp)}
                </span>
            </div>

            <p style="
                color: #555;
                font-size: 14px;
                line-height: 1.6;
            ">
                This verification code will expire in
                <strong>{settings.OTP_EXPIRE_MINUTES} minutes</strong>.
            </p>

            <p style="
                color: #999;
                font-size: 13px;
                line-height: 1.6;
            ">
                If you did not request a password reset,
                you can safely ignore this email.
            </p>

            <hr style="
                border: none;
                border-top: 1px solid #e0e0e0;
                margin: 28px 0;
            ">

            <p style="
                color: #aaa;
                font-size: 12px;
                text-align: center;
                margin: 0;
            ">
                Doctor Finder
            </p>

            <p style="
                color: #bbb;
                font-size: 11px;
                text-align: center;
                margin-top: 6px;
            ">
                Online doctor appointments and communication
            </p>

        </div>
    </div>
    """

    return _send_email(
        to_email=to_email,
        subject="Doctor Finder – Your Password Reset Code",
        html_body=html_body,
    )


def send_welcome_email(
    to_email: str,
    first_name: str,
    last_name: str,
) -> bool:
    """
    Send welcome email after successful account registration.
    """

    full_name = escape(f"{first_name} {last_name}")

    html_body = f"""
    <div style="
        font-family: Arial, sans-serif;
        max-width: 480px;
        margin: 40px auto;
        background: #ffffff;
    ">

        <div style="
            background: #1565C0;
            padding: 28px;
            border-radius: 12px 12px 0 0;
            text-align: center;
        ">
            <h1 style="
                color: #ffffff;
                margin: 0;
                font-size: 28px;
            ">
                Welcome to Doctor Finder
            </h1>

            <p style="
                color: #BBDEFB;
                margin: 8px 0 0;
                font-size: 15px;
            ">
                Your healthcare appointment platform
            </p>
        </div>

        <div style="
            background: #f5f7fa;
            padding: 32px;
            border-radius: 0 0 12px 12px;
        ">

            <p style="
                color: #333;
                font-size: 16px;
            ">
                Hi <strong>{full_name}</strong>,
            </p>

            <p style="
                color: #555;
                font-size: 15px;
                line-height: 1.7;
            ">
                Welcome to <strong>Doctor Finder</strong>.
                Your account has been created successfully.
            </p>

            <p style="
                color: #555;
                font-size: 15px;
                line-height: 1.7;
            ">
                With Doctor Finder, you can easily find doctors,
                book appointments online, and communicate with
                the clinic's secretary when you need assistance.
            </p>

            <div style="
                background: #ffffff;
                border-radius: 10px;
                padding: 20px;
                margin: 24px 0;
            ">

                <p style="
                    color: #1565C0;
                    font-weight: bold;
                    margin-top: 0;
                ">
                    What you can do:
                </p>

                <p style="color: #555; font-size: 14px;">
                    • Find doctors and available appointments
                </p>

                <p style="color: #555; font-size: 14px;">
                    • Book your appointment online
                </p>

                <p style="color: #555; font-size: 14px;">
                    • Manage your upcoming appointments
                </p>

                <p style="color: #555; font-size: 14px;">
                    • Contact the clinic secretary
                </p>

            </div>

            <p style="
                color: #555;
                font-size: 15px;
                line-height: 1.6;
            ">
                Thank you for choosing Doctor Finder.
            </p>

            <hr style="
                border: none;
                border-top: 1px solid #e0e0e0;
                margin: 28px 0;
            ">

            <p style="
                color: #aaa;
                font-size: 12px;
                text-align: center;
                margin: 0;
            ">
                Doctor Finder
            </p>

            <p style="
                color: #bbb;
                font-size: 11px;
                text-align: center;
                margin-top: 6px;
            ">
                Find a doctor. Book an appointment. Get care.
            </p>

        </div>
    </div>
    """

    return _send_email(
        to_email=to_email,
        subject="Welcome to Doctor Finder",
        html_body=html_body,
    )


def send_password_changed_email(
    to_email: str,
    first_name: str,
    last_name: str,
) -> bool:
    """
    Notify the user after successfully changing their password.
    """

    full_name = escape(f"{first_name} {last_name}")

    html_body = f"""
    <div style="
        font-family: Arial, sans-serif;
        max-width: 480px;
        margin: 40px auto;
        background: #ffffff;
    ">

        <div style="
            background: #1565C0;
            padding: 28px;
            border-radius: 12px 12px 0 0;
            text-align: center;
        ">
            <h1 style="
                color: #ffffff;
                margin: 0;
                font-size: 26px;
            ">
                Doctor Finder
            </h1>

            <p style="
                color: #BBDEFB;
                margin: 8px 0 0;
                font-size: 15px;
            ">
                Password Updated
            </p>
        </div>

        <div style="
            background: #f5f7fa;
            padding: 32px;
            border-radius: 0 0 12px 12px;
        ">

            <p style="
                color: #333;
                font-size: 16px;
            ">
                Hi <strong>{full_name}</strong>,
            </p>

            <p style="
                color: #555;
                font-size: 15px;
                line-height: 1.7;
            ">
                Your Doctor Finder account password has been
                changed successfully.
            </p>

            <div style="
                background: #ffffff;
                border-left: 4px solid #1565C0;
                border-radius: 8px;
                padding: 18px;
                margin: 24px 0;
            ">

                <p style="
                    color: #555;
                    font-size: 14px;
                    margin: 0;
                    line-height: 1.6;
                ">
                    If you made this change, no further action is required.
                </p>

            </div>

            <p style="
                color: #999;
                font-size: 13px;
                line-height: 1.6;
            ">
                If you did not change your password,
                please contact the Doctor Finder support team
                as soon as possible.
            </p>

            <hr style="
                border: none;
                border-top: 1px solid #e0e0e0;
                margin: 28px 0;
            ">

            <p style="
                color: #aaa;
                font-size: 12px;
                text-align: center;
                margin: 0;
            ">
                Doctor Finder
            </p>

            <p style="
                color: #bbb;
                font-size: 11px;
                text-align: center;
                margin-top: 6px;
            ">
                Online doctor appointments and communication
            </p>

        </div>
    </div>
    """

    return _send_email(
        to_email=to_email,
        subject="Doctor Finder – Your Password Was Changed",
        html_body=html_body,
    )