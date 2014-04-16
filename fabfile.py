from __future__ import with_statement
from fabric.api import *

import uuid

env.roledefs = {
    'staging': ['wagtailsite@django-staging.torchbox.com'],
    'production': ['wagtailsite@by-web-2.torchbox.com'],
}

# TODO: a nicer dict of settings
# DATABASES = {
#     'staging':{
#         'name': 'tbxwagtail',
#         'user': 'tbxwagtail',
#     }
#     'production':{
#         'host': 'by-postgres-a.torchbox.com',
#         'name': 'wagtail-torchbox',
#         'user': 'tbxwagtail',
#     }
# }

PROJECT = "wagtail-wagtailsite"
STAGING_DB_USERNAME = "wagtailsite"
STAGING_DB_SERVER = "localhost"
LIVE_DB_USERNAME = "wagtailsite"
LIVE_DB_SERVER = "by-postgres-a"
DB_NAME = "wagtail-wagtailsite"
LOCAL_DUMP_PATH = "~/"
REMOTE_DUMP_PATH = "~/"


@roles('staging')
def deploy_staging():
    with cd('/usr/local/django/wagtailsite/'):
        run("git pull")
        run("git submodule update")
        run("/usr/local/django/virtualenvs/wagtailsite/bin/pip install -r requirements/production.txt")
        run("/usr/local/django/virtualenvs/wagtailsite/bin/python manage.py syncdb --settings=conf.settings.production --noinput")
        run("/usr/local/django/virtualenvs/wagtailsite/bin/python manage.py migrate --settings=conf.settings.production --noinput")
        run("/usr/local/django/virtualenvs/wagtailsite/bin/python manage.py collectstatic --settings=conf.settings.production --noinput")
        run("/usr/local/django/virtualenvs/wagtailsite/bin/python manage.py compress --force --settings=conf.settings.production")

    run("sudo /usr/bin/supervisorctl restart wagtailsite")

@roles('production')
def deploy():
    with cd('/usr/local/django/wagtailsite/'):
        run("git pull")
        run("git submodule update")

        run("/usr/local/django/virtualenvs/wagtailsite/bin/pip install -r requirements/production.txt")
        run("/usr/local/django/virtualenvs/wagtailsite/bin/python manage.py syncdb --settings=conf.settings.production --noinput")
        run("/usr/local/django/virtualenvs/wagtailsite/bin/python manage.py migrate --settings=conf.settings.production --noinput")
        run("/usr/local/django/virtualenvs/wagtailsite/bin/python manage.py collectstatic --settings=conf.settings.production --noinput")
        run("/usr/local/django/virtualenvs/wagtailsite/bin/python manage.py compress --settings=conf.settings.production")

    sudo("/usr/bin/supervisorctl restart wagtailsite")

# @roles('production')
# def pull_live_data():
#     filename = "%s-%s.sql" % (DB_NAME, uuid.uuid4())
#     local_path = "%s%s" % (LOCAL_DUMP_PATH, filename)
#     remote_path = "%s%s" % (REMOTE_DUMP_PATH, filename)
#     local_db_backup_path = "%svagrant-%s-%s.sql" % (LOCAL_DUMP_PATH, DB_NAME, uuid.uuid4())

#     run('pg_dump -U%s -h %s -xOf %s' % (LIVE_DB_USERNAME, LIVE_DB_SERVER, remote_path))
#     run('gzip %s' % remote_path)
#     get("%s.gz" % remote_path, "%s.gz" % local_path)
#     run('rm %s.gz' % remote_path)
    
#     local('pg_dump -Upostgres -xOf %s %s' % (local_db_backup_path, DB_NAME))
#     puts('Previous local database backed up to %s' % local_db_backup_path)
    
#     local('dropdb -Upostgres %s' % DB_NAME)
#     local('createdb -Upostgres %s' % DB_NAME)
#     local('gunzip %s.gz' % local_path)
#     local('psql -Upostgres %s -f %s' % (DB_NAME, local_path))
#     local ('rm %s' % local_path)

@roles('staging')
def pull_staging_data():
    filename = "%s-%s.sql" % (DB_NAME, uuid.uuid4())
    local_path = "%s%s" % (LOCAL_DUMP_PATH, filename)
    remote_path = "%s%s" % (REMOTE_DUMP_PATH, filename)
    local_db_backup_path = "%svagrant-%s-%s.sql" % (LOCAL_DUMP_PATH, DB_NAME, uuid.uuid4())

    run('pg_dump -U%s -h %s -xOf %s' % (STAGING_DB_USERNAME, STAGING_DB_SERVER, remote_path))
    run('gzip %s' % remote_path)
    get("%s.gz" % remote_path, "%s.gz" % local_path)
    run('rm %s.gz' % remote_path)
    
    local('pg_dump -Upostgres -xOf %s %s' % (local_db_backup_path, DB_NAME))
    puts('Previous local database backed up to %s' % local_db_backup_path)
    
    local('dropdb -Upostgres %s' % DB_NAME)
    local('createdb -Upostgres %s' % DB_NAME)
    local('gunzip %s.gz' % local_path)
    local('psql -Upostgres %s -f %s' % (DB_NAME, local_path))
    local ('rm %s' % local_path)


@roles('staging')
def push_staging_media():
    media_filename = "%s-%s-media.tar" % (PROJECT, uuid.uuid4())
    local_media_dump = "%s%s" % (LOCAL_DUMP_PATH, media_filename)
    remote_media_dump = "%s%s" % (REMOTE_DUMP_PATH, media_filename)

    # tar and upload media
    local('tar -cvf %s media' % local_media_dump)
    local('gzip %s' % local_media_dump)
    put('%s.gz' % local_media_dump, '%s.gz' % remote_media_dump)

    # unzip everything
    with cd('/usr/local/django/wagtailsite/'):
        run('rm -rf media')
        run('mv %s.gz .' % remote_media_dump)
        run('tar -xzvf %s.gz' % media_filename)
        run('rm %s.gz' % media_filename)

@roles('staging')
def pull_staging_media():
    media_filename = "%s-%s-media.tar" % (PROJECT, uuid.uuid4())
    local_media_dump = "%s%s" % (LOCAL_DUMP_PATH, media_filename)
    remote_media_dump = "%s%s" % (REMOTE_DUMP_PATH, media_filename)

    # tar and download media
    with cd('/usr/local/django/wagtailsite/'):
        run('tar -cvf %s media' % remote_media_dump)
        run('gzip %s' % remote_media_dump)
    
    get('%s.gz' % remote_media_dump, '%s.gz' % local_media_dump)

    local('rm -rf media')
    local('mv %s.gz .' % local_media_dump)
    local('tar -xzvf %s.gz' % media_filename)
    local('rm %s.gz' % media_filename)


@roles('staging')
def push_staging_data():
    filename = "%s-%s.sql" % (DB_NAME, uuid.uuid4())
    local_path = "%s%s" % (LOCAL_DUMP_PATH, filename)
    remote_path = "%s%s" % (REMOTE_DUMP_PATH, filename)
    staging_db_backup_path = "%s%s-%s.sql" % (REMOTE_DUMP_PATH, DB_NAME, uuid.uuid4())

    # dump and upload db
    local('pg_dump -Upostgres -xOf %s %s' % (local_path, DB_NAME))
    local('gzip %s' % local_path)
    put("%s.gz" % local_path, "%s.gz" % remote_path)

    run('pg_dump -xO -U%s -h %s -f %s' % (STAGING_DB_USERNAME, STAGING_DB_SERVER, staging_db_backup_path))
    puts('Previous staging database backed up to %s' % staging_db_backup_path)
    
    run('gunzip %s.gz' % remote_path)
    run('psql -U%s -h %s -c "DROP SCHEMA public CASCADE"' % (STAGING_DB_USERNAME, STAGING_DB_SERVER))
    run('psql -U%s -h %s -c "CREATE SCHEMA public"' % (STAGING_DB_USERNAME, STAGING_DB_SERVER))
    run('psql -U%s -h %s -f %s' % (STAGING_DB_USERNAME, STAGING_DB_SERVER, remote_path))
    run('rm %s' % remote_path)
