# Generated by Django 4.1.7 on 2023-04-15 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0003_remove_user_password'),
    ]

    operations = [
        migrations.CreateModel(
            name='review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(default='pavan', max_length=30)),
                ('content', models.TextField(default='some content')),
                ('reviews', models.TextField(default='some review')),
            ],
        ),
    ]