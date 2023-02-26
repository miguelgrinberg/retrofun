import csv
from sqlalchemy import select
from db import Session
from models import BlogArticle, Language


def main():
    with Session() as session:
        with session.begin():
            all_articles = {}
            all_languages = {}

            with open('articles.csv') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    article = all_articles.get(row['title'])
                    if article is None:
                        article = session.scalar(select(BlogArticle).where(
                            BlogArticle.title == row['title']))
                        all_articles[article.title] = article

                    language = all_languages.get(row['language'])
                    if language is None:
                        language = session.scalar(select(Language).where(
                            Language.name == row['language']))
                        if language is None:
                            language = Language(name=row['language'])
                            session.add(language)
                        all_languages[language.name] = language
                    article.language = language

                    if row['translation_of']:
                        translation_of = all_articles.get(
                            row['translation_of'])
                        if translation_of is None:
                            translation_of = session.scalar(select(
                                BlogArticle).where(BlogArticle.title ==
                                                   row['translation_of']))
                            all_articles[article.title] = article
                        article.translation_of = translation_of


if __name__ == '__main__':
    main()
