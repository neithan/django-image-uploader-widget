# Generated by Django 4.1 on 2022-09-08 17:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('demo_application', '0004_testnonrequiredinline_alter_testnonrequired_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestNonRequiredTabularInline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Test Non Required Tabular Inline',
            },
        ),
        migrations.CreateModel(
            name='TestNonRequiredTabularInlineItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='', verbose_name='Image')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='demo_application.testnonrequiredtabularinline')),
            ],
        ),
    ]
