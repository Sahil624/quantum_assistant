# Generated by Django 5.1.1 on 2024-10-02 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user_course", "0002_learningobject_completed_on_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="learningobject",
            name="completed_on",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]