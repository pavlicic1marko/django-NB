from django.db import migrations, models
from django.utils.text import slugify


def populate_news_slugs(apps, schema_editor):
    News = apps.get_model("webapp", "News")

    for article in News.objects.order_by("id"):
        base_slug = slugify(article.title)[:200] or "news"
        slug = base_slug
        suffix = 2
        while News.objects.filter(language=article.language, slug=slug).exclude(pk=article.pk).exists():
            suffix_text = f"-{suffix}"
            slug = f"{base_slug[:220 - len(suffix_text)]}{suffix_text}"
            suffix += 1
        article.slug = slug
        article.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0007_news_language"),
    ]

    operations = [
        migrations.AddField(
            model_name="news",
            name="slug",
            field=models.SlugField(default="", editable=False, max_length=220),
            preserve_default=False,
        ),
        migrations.RunPython(populate_news_slugs, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="news",
            constraint=models.UniqueConstraint(fields=("language", "slug"), name="unique_news_language_slug"),
        ),
    ]