import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from terminaltables import AsciiTable

from superjob import get_statistics_on_programming_languages_sj


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
    params = {'text': f"{text} {language}", 'per_page': quantity_per_page, 'page': 1, 'area': moscow_id, 'date_from': date_from}
    url = 'https://api.hh.ru/vacancies/'
    vacancies = []
    while True:
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            response = response.json()
            for vacancy in response['items']:
                vacancies.append(vacancy)

            if params['page'] == response['pages'] - 1:
                break
            else:
                params['page'] += 1
        except requests.exceptions.RequestException as e:
            print(f"Произошла ошибка при запросе: {e}")
            break

    return vacancies


def predict_rub_salary(vacancy):
    rub_salary = vacancy.get('salary', False)
    if not rub_salary or rub_salary['currency'] != 'RUR':
        return None
    if rub_salary['from'] and rub_salary['to']:
        return (rub_salary['from'] + rub_salary['to']) / 2
    elif rub_salary['from']:
        return rub_salary['from'] * 1.2
    elif rub_salary['to']:
        return rub_salary['to'] * 0.8


def get_statistics_on_programming_languages():
    vacancies_by_language = group_vacancies_by_language_hh()
    staticstics_languages = {}
    for language in vacancies_by_language.keys():
        vacancies_found = len(vacancies_by_language[language])
        if vacancies_found < 100:
            continue
        salaries_by_vacancy = [predict_rub_salary(vacancy) for vacancy in vacancies_by_language[language]]
        salaries_by_vacancy = [salary for salary in salaries_by_vacancy if salary]
        average_salary = sum(salaries_by_vacancy) / len(salaries_by_vacancy)
        staticstics_languages[language] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": len(salaries_by_vacancy),
            "average_salary": int(average_salary),
        }
    title = '-HeadHunter Moscow-'
    table_data = (
        ('Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'),
        *((language, value['vacancies_found'], value['vacancies_processed'], value['average_salary'])
          for language, value in staticstics_languages.items())
    )

    table = AsciiTable(table_data, title=title)
    print(f'{table.table} \n')


if __name__ == '__main__':
    load_dotenv()
    get_statistics_on_programming_languages()
    print(get_statistics_on_programming_languages_sj(os.getenv('SECRET_KEY')))
