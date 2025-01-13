import os
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable

load_dotenv()


def get_popular_languages_sj():
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
    for language in popular_languages.keys():
        popular_languages[language] = get_vacancies_sj(language)

    return popular_languages


def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] != 'rub':
        return None
    if vacancy['payment_from'] and vacancy['payment_to']:
        return (vacancy['payment_from'] + vacancy['payment_to']) / 2
    elif vacancy['payment_from']:
        return vacancy['payment_from'] * 1.2
    elif vacancy['payment_to']:
        return vacancy['payment_to'] * 0.8


def get_vacancies_sj(languange: str):
    vacancies_sj = []
    secret_key = os.getenv('SECRET_KEY')
    headers = {'X-Api-App-Id': secret_key}
    date_from = int((datetime.now() - timedelta(days=30)).timestamp())
    page = 0
    while True:
        try:
            params = {'keywords': languange, 'catalogues': 48, 'town': 'Москва', 'page': page, 'count': 40,
                      'date_published[from]': date_from}
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
            break

    return vacancies_sj


def get_statistics_on_programming_languages_sj():
    popular_languages = get_popular_languages_sj()
    staticstics_languages = {}
    for language in popular_languages.keys():
        vacancies_found = len(popular_languages[language])
        if vacancies_found == 0:
            continue
        total_salary = [predict_rub_salary_sj(vacancy) for vacancy in popular_languages[language]]
        total_salary = [salary for salary in total_salary if salary]
        average_salary = sum(total_salary) / len(total_salary) if len(total_salary) > 0 else 0
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
