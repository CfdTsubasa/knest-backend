# Generated manually to remove Tag and UserTag models

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interests', '0005_interestcategory_interestsubcategory_interesttag_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserTag',
        ),
        migrations.DeleteModel(
            name='Tag',
        ),
    ] 