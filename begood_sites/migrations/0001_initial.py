# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.manager
import django.contrib.sites.managers
import begood_sites.fields


class Migration(migrations.Migration):

    dependencies = [
        ('begood', '0005_auto_20161109_1140'),
        ('sites', '0001_initial'),
        ('reversion', '0001_squashed_0004_auto_20160611_1202'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('site', models.OneToOneField(related_name='settings', primary_key=True, serialize=False, to='sites.Site')),
                ('extra_html_head', models.TextField(verbose_name='Extra HTML-head', blank=True)),
                ('stylesheet', models.FilePathField(path=b'/Users/andreas/repositories/agoodid/stageroom/xcalibur/static/less', verbose_name='Stylesheet to use', match=b'theme.*?', blank=True)),
                ('language_code', models.CharField(default=b'sv', max_length=10, verbose_name='language', choices=[(b'sv', b'Swedish')])),
                ('image_quality', models.IntegerField(blank=True, null=True, verbose_name='image quality', choices=[(65, 'Low (fastest)'), (75, 'Normal'), (90, 'Very high (slowest)')])),
                ('basic_authentication_username', models.CharField(max_length=255, verbose_name='username', blank=True)),
                ('basic_authentication_password', models.CharField(max_length=255, verbose_name='password', blank=True)),
                ('root_site', models.ForeignKey(related_name='children', default=1, to='sites.Site')),
                ('simple_input', models.ForeignKey(related_name='+', verbose_name='SimpleInput + User template', blank=True, to='begood.Template', null=True)),
                ('template_404', models.ForeignKey(related_name='+', verbose_name='404 template', blank=True, to='begood.Template', null=True)),
                ('template_search', models.ForeignKey(related_name='+', verbose_name='search template', blank=True, to='begood.Template', null=True)),
            ],
            options={
                'verbose_name': 'site settings',
                'verbose_name_plural': 'site settings',
            },
        ),
        migrations.CreateModel(
            name='VersionSite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('revision', models.ForeignKey(related_name='versionsites', to='reversion.Revision')),
                ('site', begood_sites.fields.SingleSiteField(to='sites.Site')),
            ],
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('on_site', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='versionsite',
            unique_together=set([('revision', 'site')]),
        ),
    ]
