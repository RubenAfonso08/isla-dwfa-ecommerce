from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0002_create_gestores_group"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="receipt_sent_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]