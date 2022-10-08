# Generated by Django 3.2.15 on 2022-10-05 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_auto_20221005_1644'),
    ]

    operations = [
        migrations.CreateModel(
            name='Watchlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('auc_id', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='bids',
            name='auction_id',
            field=models.IntegerField(),
        ),
    ]