from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64
from email.mime.text import MIMEText

class GoogleIntegrations:
    def __init__(self, credentials_path='credentials.json', token_path='token.json'):
        self.creds = Credentials.from_authorized_user_file(token_path)
        self.calendar_service = build('calendar', 'v3', credentials=self.creds)
        self.gmail_service = build('gmail', 'v1', credentials=self.creds)

    def get_calendar_events(self, max_results=10):
        events_result = self.calendar_service.events().list(
            calendarId='primary', timeMin='now', maxResults=max_results, singleEvents=True,
            orderBy='startTime'
        ).execute()
        return events_result.get('items', [])

    def add_calendar_event(self, summary, start_time, end_time):
        event = {
            'summary': summary,
            'start': {'dateTime': start_time, 'timeZone': 'UTC'},
            'end': {'dateTime': end_time, 'timeZone': 'UTC'},
        }
        self.calendar_service.events().insert(calendarId='primary', body=event).execute()

    def send_email(self, to, subject, body):
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        self.gmail_service.users().messages().send(userId='me', body={'raw': raw}).execute()
