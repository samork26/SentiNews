# Generated by Django 5.1.6 on 2025-03-03 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocalNews',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('url', models.URLField(unique=True)),
                ('source', models.CharField(max_length=100)),
                ('published_at', models.DateTimeField()),
                ('category', models.CharField(max_length=50)),
                ('sentiment', models.CharField(blank=True, max_length=20, null=True)),
                ('location', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterModelOptions(
            name='newsarticle',
            options={},
        ),
    ]
