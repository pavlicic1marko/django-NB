from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0008_news_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="news",
            name="alt_text",
            field=models.CharField(default="", max_length=255),
            preserve_default=False,
        ),
    ]