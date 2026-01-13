import datetime
import platform
from zoneinfo import ZoneInfo  # Available in Python 3.9+

def schedule_teams_meeting(subject, date_input, start_time_input, duration, attendees_input):
    """
    Schedule a Teams meeting. On Windows, uses Outlook COM. On Linux/other platforms,
    saves meeting details to database only (Outlook integration not available).
    """
    # Check if running on Windows
    if platform.system() == "Windows":
        try:
            # pywin32 is required for Windows Outlook integration
            # Install with: pip install pywin32
            import pythoncom  # type: ignore
            import win32com.client  # type: ignore
            
            pythoncom.CoInitialize()
            outlook = win32com.client.Dispatch("Outlook.Application")
            meeting = outlook.CreateItem(1)  # olAppointmentItem

            # Attach timezone (Asia/Kolkata for IST)
            tz = ZoneInfo("Asia/Kolkata")
            start_datetime = datetime.datetime.strptime(
                f"{date_input} {start_time_input}", "%Y-%m-%d %H:%M"
            ).replace(tzinfo=tz)

            attendees = [email.strip() for email in attendees_input.split(",")]

            # Set meeting details
            meeting.Subject = subject
            meeting.Start = start_datetime.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S")
            meeting.Duration = duration
            meeting.Location = "Microsoft Teams Meeting"
            meeting.Body = "This meeting is scheduled via Python script using your organization email."
            meeting.MeetingStatus = 1  # olMeeting

            for email in attendees:
                meeting.Recipients.Add(email)

            # Resolve recipients to ensure they're valid
            meeting.Recipients.ResolveAll()
            
            # Save the meeting first
            meeting.Save()
            
            # Send the meeting invitation
            # Note: This will send immediately if Outlook is configured
            # If Outlook requires user confirmation, the meeting will be in Outbox
            meeting.Send()
            
            pythoncom.CoUninitialize()
            return {"success": True, "message": "✅ Teams meeting scheduled and sent successfully! Check your Outlook Outbox/Sent Items."}
            
        except ImportError:
            # win32com not available
            return {
                "success": False, 
                "message": "❌ Outlook integration not available. Meeting details saved to database."
            }
        except Exception as e:
            pythoncom.CoUninitialize()
            return {"success": False, "message": f"❌ Failed to schedule meeting: {e}"}
    else:
        # On Linux/other platforms, just save to database
        # The meeting details are already saved in main.py before calling this function
        return {
            "success": True, 
            "message": "✅ Meeting details saved. Note: Outlook integration is only available on Windows."
        }
if __name__ == "__main__":
    print("📅 Outlook Teams Scheduler CLI Test\n")
    subject = input("Enter meeting subject: ")
    date_input = input("Enter meeting date (YYYY-MM-DD): ")
    start_time_input = input("Enter start time (HH:MM, 24-hour format): ")
    duration = int(input("Enter duration in minutes: "))
    attendees_input = input("Enter attendee emails separated by commas: ")

    result = schedule_teams_meeting(subject, date_input, start_time_input, duration, attendees_input)
    print(result["message"])