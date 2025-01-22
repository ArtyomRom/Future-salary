import os
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable

from superjob import get_statistics_on_programming_languages_sj, predict_rub_salary


def group_vacancies_by_language_hh():
    vacancies_by_language = {
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
    for language in vacancies_by_language.keys():
        vacancies_by_language[language] = get_vacancies_by_language(language)

    return vacancies_by_language


def get_vacancies_by_language(language: str):
    today = datetime.today()
    text = 'программист'
    moscow_id = 1
    quantity_per_page = 100
    date_from = (today - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S")
    params = {'text': f"{text} {language}", 'per_page': quantity_per_page, 'page': 1, 'area': moscow_id,
              'date_from': date_from}
    url = 'https://api.hh.ru/vacancies/'
    vacancies_hh = {
        'vacancies': [],
        'found_vacancies': 0,
    }
    while True:
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            response = response.json()
            for vacancy in response['items']:
                vacancies_hh['vacancies'].append(vacancy)
                if not vacancies_hh['found_vacancies']:
                    vacancies_hh['found_vacancies'] = response['found']

            if params['page'] >= response['pages']:
                break

            else:
                params['page'] += 1
        except requests.exceptions.RequestException as e:
            print(f"Произошла ошибка при запросе: {e}")
            break
    return vacancies_hh


def get_statistics_on_programming_languages():
    vacancies_by_language = group_vacancies_by_language_hh()
    staticstics_languages = {}
    minimum_number_of_vacancies = 100
    for language, data_vacancies in vacancies_by_language.items():
        vacancies_found = data_vacancies['found_vacancies']
        if vacancies_found < minimum_number_of_vacancies:
            continue
        salaries_by_vacancy = [predict_rub_salary(vacancy['salary'], vacancy['salary']['from'], vacancy['salary']['to'])
                               for
                               vacancy in data_vacancies['vacancies'] if vacancy.get('salary', False)]

        salaries_by_vacancy = [salary for salary in salaries_by_vacancy if salary]
        average_salary = sum(salaries_by_vacancy) / len(salaries_by_vacancy) if salaries_by_vacancy else 0
        staticstics_languages[language] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": len(salaries_by_vacancy),
            "average_salary": int(average_salary),
        }
    return staticstics_languages


def show_statistics(title, statistics):
    table_data = (
        ('Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'),
        *((language, value['vacancies_found'], value['vacancies_processed'], value['average_salary'])
          for language, value in statistics.items())
    )

    table = AsciiTable(table_data, title=title)
    print(f'{table.table} \n')


if __name__ == '__main__':
    load_dotenv()
    show_statistics('-HeadHunter Moscow-', get_statistics_on_programming_languages())
    show_statistics('-SuperJob Moscow-',
                    get_statistics_on_programming_languages_sj(os.getenv('SUPERJOB_TOKEN')))
