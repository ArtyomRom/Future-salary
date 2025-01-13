import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flashtext import KeywordProcessor
from terminaltables import AsciiTable

load_dotenv()

def predict_salary(salary_from, salary_to):
    return None if salary_from == 0 else (salary_from * 1.2 + salary_to * 0.8) / 2


def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] == 'rub':
        averange_salary = predict_salary(vacancy['payment_from'], vacancy['payment_to'])
        return averange_salary
    return None


def get_vacancies_sj():
    vacancies_sj = []
    secret_key = os.getenv('SECRET_KEY')
    headers = {'X-Api-App-Id': secret_key}
    date_from = int((datetime.now() - timedelta(days=30)).timestamp())
    page = 0
    while True:
        try:
            params = {'catalogues': 48, 'town': 'Москва', 'page': page, 'count': 40, 'date_published[from]': date_from}
            response = requests.get(f'https://api.superjob.ru/2.0/vacancies/', headers=headers, params=params)
            response.raise_for_status()
            response = response.json()
            for vacancy in response['objects']:
                vacancies_sj.append(vacancy)

            if not response.get('more', False):
                break
            page += 1
        except requests.exceptions.RequestException as e:
            print(f"Произошла ошибка при запросе: {e}")


    return vacancies_sj



def get_popular_languages_sj(vacancies):
    keyword_processor = KeywordProcessor()
    popular_languages = {
        'JavaScript': [],
        'Java': [],
        'Python': [],
        'Ruby': [],
        'PHP': [],
        'C++': [],
        'C#': [],
        'C': [],
        'GO': [],
    }
    keyword_processor.add_keywords_from_list(list(popular_languages.keys()))

    for vacancy in vacancies:
        article = vacancy['vacancyRichText']
        find_keywords = keyword_processor.extract_keywords(article)
        for keyword in find_keywords:
            popular_languages[keyword].append(vacancy)

    return popular_languages



def get_statistics_on_programming_languages_sj():
    languages = ['JavaScript', 'Python', 'Ruby', 'PHP', 'C++', 'C#', 'GO', 'Java', 'C']
    vacancies_sj = get_popular_languages_sj(get_vacancies_sj())
    staticstics_languages = {}
    for language in languages:
        vacancies_found = len(vacancies_sj[language])
        if vacancies_found == 0:
            continue
        total_salary = [predict_rub_salary_sj(vacancy) for vacancy in vacancies_sj[language] if
                        isinstance(predict_rub_salary_sj(vacancy), float)]
        average_salary = sum(total_salary) / len(total_salary) if len(total_salary) != 0 else "Нет данных о зарплате"
        staticstics_languages[language] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": len(total_salary),
            "average_salary": int(average_salary) if isinstance(average_salary, float) else average_salary,
        }
    title = '-SuperJob Moscow-'
    table_data = (
        ('Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'),
        *((language, value['vacancies_found'], value['vacancies_processed'], value['average_salary'])
          for language, value in staticstics_languages.items())
    )

    table = AsciiTable(table_data, title=title)
    print(table.table)



if __name__ == '__main__':
    get_statistics_on_programming_languages_sj()
