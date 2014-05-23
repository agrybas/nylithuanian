from __future__ import absolute_import

from .celery import app
from .models import Article, ArticleSource
from users.models import User

from time import mktime
from datetime import datetime
import feedparser
import pytz
import logging
from django.conf import settings
from django.core.mail import mail_admins
from django.template import Context
from django.template.loader import get_template

if settings.DEBUG:
    logger = logging.getLogger('debug.' + __name__)
else:
    logger = logging.getLogger('production.' + __name__)

SOURCES = {
           'http://www.delfi.lt/rss/feeds/emigrants.xml' : 'delfi.lt',
           'http://www.balsas.lt' : 'balsas.lt',
           'http://www.lrytas.lt' : 'lrytas.lt',
           }

TIMEZONES = {
             'http://www.delfi.lt/rss/feeds/emigrants.xml' : 'Europe/Vilnius',
             'http://www.balsas.lt' : 'Europe/Vilnius',
             'http://www.lrytas.lt' : 'Europe/Vilnius',
             }

@app.task
def pull_rss_articles(path):
    parser = feedparser.parse(path)
    source = ArticleSource.objects.get(title = SOURCES[parser.feed.link])
    logger.info(u'Found {0} articles from {1} RSS feed...'.format(len(parser.entries), source.title))
    
    logger.debug(u'Looking for articles of source_id={0}'.format(source.id))
    articles = Article.objects.filter(source_id=source.id).order_by('-create_date')
    logger.info(u'Found {0} articles from {1} currently stored in local database'.format(len(articles), SOURCES[parser.feed.link]))
    
    tz = pytz.timezone(TIMEZONES[parser.feed.link])
    logger.debug(u'Will assign {0} timezone for publishing dates of retrieved RSS articles'.format(TIMEZONES[parser.feed.link]))
    
    addedArticles = []
    
    # if there exist articles in the database from this source
    if articles:
        recent_article = articles[0]
        recent_pub_date = recent_article.create_date.replace(tzinfo = pytz.utc)
        logger.debug(u'Most recent article: "{0}", published on {1}'.format(recent_article.title, recent_pub_date))
        
        for entry in parser.entries:
            pub_date = datetime.fromtimestamp(mktime(entry.published_parsed))
            pub_date = tz.normalize(tz.localize(pub_date)).astimezone(pytz.utc)
            
            # insert only newly published articles since last run
            if pub_date > recent_pub_date:
                logger.info(u'Found article "{0}" published on {1}. Adding to database...'.format(entry.title, pub_date))
                
                article = Article(
                                  user = User.objects.get(id=1),
                                  title = entry.title,
                                  body = entry.description,
                                  create_date = pub_date,
                                  #create_date = timezone.now(),
                                  #modify_date = timezone.now(),
                                  source = source,
                                  external_link = entry.link,
                                  is_approved = True,
                                  )
                article.save()
#                transaction.enter_transaction_management()
#                transaction.commit()
                addedArticles.append(article)
                
                logger.info(u'Article added successfully.')
        
        if addedArticles:
            logger.info('{0} articles have been added.'.format(len(addedArticles)))
        else:
            logger.info('No new articles found in the feed.')
    
    # if there are no articles in the database from this source - first time run
    else:
        # insert all articles found in the feed
        logger.info(u'Adding all articles from {0} feed to the database...'.format(SOURCES[parser.feed.link]))
        
        for entry in parser.entries:
            pub_date = datetime.fromtimestamp(mktime(entry.published_parsed))
            pub_date = tz.normalize(tz.localize(pub_date)).astimezone(pytz.utc)
            
            logger.info(u'Adding article "{0}"...'.format(entry.title))
            
            article = Article(
                                  user = User.objects.get(id=1),
                                  title = entry.title,
                                  body = entry.description,
                                  create_date = pub_date,
                                  #create_date = timezone.now(),
                                  #modify_date = timezone.now(),
                                  source = source,
                                  external_link = entry.link,
                                  is_approved = True,
                                  )
            article.save()
#            transaction.enter_transaction_management()
#            transaction.commit()
            addedArticles.append(article)
            
            logger.info(u'Article added successfully.')
        
        logger.info('{0} articles have been added.'.format(len(addedArticles)))

    if addedArticles:
        # E-mail admins to confirm profile upgrade
        plainText = get_template('emails/added_rss_articles.txt')
        htmlText = get_template('emails/added_rss_articles.html')
        subject = u'Nauji RSS straipsniai'
        c = Context({
                     'source' : source.title,
                     'articles' : addedArticles,
                     })
        
        mail_admins(subject=subject, message=plainText.render(c), html_message=htmlText.render(c))
