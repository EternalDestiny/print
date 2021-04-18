# Generated by Django 3.1.7 on 2021-04-18 07:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Print',
            fields=[
                ('gcodefile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True,
                                                   related_name='print', serialize=False, to='app.gcodefile')),
                ('estimatedPrintTime', models.IntegerField(blank=True, default=0, null=True)),
                ('averagePrintTime', models.IntegerField(blank=True, default=0, null=True)),
                ('completion', models.FloatField(blank=True, default=0, null=True)),
                ('printTime', models.IntegerField(blank=True, default=0, null=True)),
                ('printTimeLeft', models.IntegerField(blank=True, default=0, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Printer',
            fields=[
                ('printer_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('operational', models.BooleanField(default=False)),
                ('printing', models.BooleanField(default=False)),
                ('cancelling', models.BooleanField(default=False)),
                ('pausing', models.BooleanField(default=False)),
                ('resuming', models.BooleanField(default=False)),
                ('finishing', models.BooleanField(default=False)),
                ('closedOrError', models.BooleanField(default=True)),
                ('error', models.BooleanField(default=False)),
                ('paused', models.BooleanField(default=False)),
                ('ready', models.BooleanField(default=False)),
                ('tool_temperature', models.IntegerField(blank=True, null=True)),
                ('bed_temperature', models.IntegerField(blank=True, null=True)),
                ('current_print',
                 models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                      related_name='not_used', to='chat.print')),
            ],
        ),
    ]
