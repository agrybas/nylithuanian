#encoding=utf-8
import icalendar
import logging
import nylithuanian.settings as settings
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.utils.encoding import smart_text
from django.template import defaultfilters
from .models import Event

DOMAIN = 'http://dev.nylithuanian.org/'

if settings.DEBUG:
    logger = logging.getLogger('debug.' + __name__)
else:
    logger = logging.getLogger('production.' + __name__)

def generateEventFeed(event):
    logger.info(u'Generating ICS feed for event {0}...'.format(event.__unicode__()))
    
    cal = icalendar.Calendar()
    cal.add('prodid', u'-//Niujorko renginių kalendorius//LT//')
    cal.add('version', '2.0')
    cal.add('method', 'PUBLISH')
    cal.add('calscale', 'GREGORIAN')
    cal.add('x-wr-calname', event.title)
    cal.add('x-wr-timezone', settings.TIME_ZONE)
    cal.add('x-original-url', DOMAIN + 'renginiai/{0}'.format(event.id))
    
    e = icalendar.Event()
    e.add('uid', 'event_{0}@nylithuanian.org'.format(event.id))
    e.add('created', event.create_date)
    e.add('last-modified', event.modify_date)
    e.add('summary', event.title)
    e.add('description', defaultfilters.truncatewords(event.body, 100) + '\nDaugiau informacijos: http://dev.nylithuanian.org/renginiai/{0}'.format(event.id))
    e.add('sequence', event.version_number)
    e.add('class', 'PUBLIC')
    e.add('status', 'CONFIRMED')
    e.add('url', DOMAIN + 'renginiai/{0}'.format(event.id))
    
    if not event.start_date:
        logger.warning(u'Event start date is null, skipping entry in ICS feed...')
    else:
        e.add('dtstart', event.start_date)
    
    if event.end_date:
        e.add('dtend', event.end_date)
    elif event.start_date:
        e.add('dtend', event.start_date + timedelta(hours=2)) # default event length: 2 hours
  
    if event.get_full_address():
        e['location'] = icalendar.vText(event.get_full_address())
    
    if event.email_address:
        organizer = icalendar.vCalAddress("MAILTO:{0}".format(event.email_address))
        organizer.params['cn'] = icalendar.vText(event.get_organizer_full_name())
        e['organizer'] = organizer
    
    cal.add_component(e)
    
    logger.info(u'Generated ICS event feed:\n{0}'.format(smart_text(cal.to_ical())))
    
    return cal.to_ical()


def getEventIcsFeed(request, *args, **kwargs):
    event = Event.objects.get(id=kwargs['pk'])
    calendar = generateEventFeed(event)
    response = HttpResponse(calendar)
    #response['Filename'] = 'renginys.ics'
    response['Content-Disposition'] = 'inline; filename=renginys.ics'
    response['Content-Type'] = 'text/calendar; charset=utf-8'
    return response