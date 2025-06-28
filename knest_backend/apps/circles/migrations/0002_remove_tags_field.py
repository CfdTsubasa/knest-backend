# Generated manually to remove tags field

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('circles', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='circle',
            name='tags',
        ),
    ] 