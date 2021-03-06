# Generated by Django 2.1.7 on 2019-03-17 22:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SavedSearchParameters',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Letters_list', models.CharField(max_length=20)),
                ('Created_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='SavedSearchResults',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Word_name', models.CharField(max_length=20)),
                ('Missing', models.CharField(max_length=20)),
                ('Length', models.IntegerField()),
                ('Score', models.IntegerField()),
                ('Pksearch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scrabble_analytics.SavedSearchParameters')),
            ],
        ),
        migrations.CreateModel(
            name='Words',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Word_name', models.CharField(max_length=20)),
                ('Score', models.IntegerField()),
                ('Word_name_len', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='WordsSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Wordset_name', models.CharField(max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='words',
            name='Word_set',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scrabble_analytics.WordsSet'),
        ),
    ]
