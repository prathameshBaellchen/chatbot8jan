import datetime
import pythoncom
import win32com.client
from zoneinfo import ZoneInfo  # Available in Python 3.9+

def schedule_teams_meeting(subject, date_input, start_time_input, duration, attendees_input):
    try:
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

        meeting.Save()
        meeting.Send()

        return {"success": True, "message": "✅ Teams meeting scheduled successfully!"}

    except Exception as e:
        return {"success": False, "message": f"❌ Failed to schedule meeting: {e}"}

    finally:
        pythoncom.CoUninitialize()
if __name__ == "__main__":
    print("📅 Outlook Teams Scheduler CLI Test\n")
    subject = input("Enter meeting subject: ")
    date_input = input("Enter meeting date (YYYY-MM-DD): ")
    start_time_input = input("Enter start time (HH:MM, 24-hour format): ")
    duration = int(input("Enter duration in minutes: "))
    attendees_input = input("Enter attendee emails separated by commas: ")

    result = schedule_teams_meeting(subject, date_input, start_time_input, duration, attendees_input)
    print(result["message"])