# Generated by Django 4.1 on 2022-09-09 00:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demo_application', '0005_testnonrequiredtabularinline_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestRequired',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='', verbose_name='Image')),
            ],
            options={
                'verbose_name': 'Test Required',
            },
        ),
    ]
