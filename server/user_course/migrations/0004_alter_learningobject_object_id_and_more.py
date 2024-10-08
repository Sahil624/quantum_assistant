# Generated by Django 5.1.1 on 2024-10-07 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user_course", "0003_alter_learningobject_completed_on"),
    ]

    operations = [
        migrations.AlterField(
            model_name="learningobject",
            name="object_id",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name="learningobject",
            unique_together={("object_id", "course")},
        ),
    ]