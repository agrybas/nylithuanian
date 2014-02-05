"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

#from django.test import TestCase
from django.utils import unittest, timezone
from datetime import datetime
from .feeds import generateEventFeed
from .models import Event

class SingleEventCalendarFeedTest(unittest.TestCase):
    def test_generateEventFeed_simple(self):
        event = Event(title="Some title", body="Some text")
        calendar = generateEventFeed(event)
        correctICS = 'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//Niujorko rengini\xc5\xb3 kalendorius//mxm.dk//\r\nX-WR-CALNAME:Some title\r\nX-WR-TIMEZONE:America/New_York\r\nBEGIN:VEVENT\r\nSUMMARY:Some text\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n'
        self.assertEqual(calendar, correctICS)

    def test_generateEventFeed_full(self):
        event = Event(
                      title="Some title",
                      body="Some text",
                      start_date=datetime(2014, 02, 15, 14, 00, 00, tzinfo=timezone.utc),
                      end_date=datetime(2014, 02, 15, 16, 00, 00, tzinfo=timezone.utc),
                      first_name="Some first name",
                      last_name="Some last name",
                      organization_title="Some organization",
                      phone_number="+1 (123) 456-7890",
                      email_address="firstname.lastname@organization.org",
                      street_address1="First street address Apt. 77",
                      city="New York",
                      zip_code="10000",
                      state="NY",
                      country="US"
                      )
        calendar = generateEventFeed(event)
        correctICS = 'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//Niujorko rengini\xc5\xb3 kalendorius//mxm.dk//\r\nX-WR-CALNAME:Some title\r\nX-WR-TIMEZONE:America/New_York\r\nBEGIN:VEVENT\r\nSUMMARY:Some text\r\nDTSTART;VALUE=DATE-TIME:20140215T140000Z\r\nDTEND;VALUE=DATE-TIME:20140215T160000Z\r\nLOCATION:First street address Apt. 77\\, New York\\, NY\\, 10000\\, US\r\nORGANIZER;CN="Some first name Some last name, Some organization":MAILTO:fi\r\n rstname.lastname@organization.org\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n'
        self.assertEqual(calendar, correctICS)
        