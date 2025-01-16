from datetime import datetime, timedelta
from terminaltables import AsciiTable
import requests

def group_vacancies_by_language_sj(secret_key):
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
        vacancies_by_language[language] = get_vacancies_sj(language, secret_key)

    return vacancies_by_language


def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] != 'rub':
        return None
    if vacancy['payment_from'] and vacancy['payment_to']:
        return (vacancy['payment_from'] + vacancy['payment_to']) / 2
    elif vacancy['payment_from']:
        return vacancy['payment_from'] * 1.2
    elif vacancy['payment_to']:
        return vacancy['payment_to'] * 0.8


def get_vacancies_sj(languange: str, secret_key):
    vacancies_sj = []
    headers = {'X-Api-App-Id': secret_key}
    date_from = int((datetime.now() - timedelta(days=30)).timestamp())
    categoria_id = 48
    quantity_per_page = 40
    page = 0
    while True:
        try:
            params = {'keywords': languange, 'catalogues': categoria_id, 'town': 'Москва', 'page': page, 'count': quantity_per_page,
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


def get_statistics_on_programming_languages_sj(secret_key: str):
    vacancies_by_language = group_vacancies_by_language_sj(secret_key)
    staticstics_languages = {}
    for language in vacancies_by_language.keys():
        vacancies_found = len(vacancies_by_language[language])
        if vacancies_found == 0:
            continue
        salaries_by_vacancy = [predict_rub_salary_sj(vacancy) for vacancy in vacancies_by_language[language]]
        salaries_by_vacancy = [salary for salary in salaries_by_vacancy if salary]
        average_salary = sum(salaries_by_vacancy) / len(salaries_by_vacancy) if salaries_by_vacancy else 0
        staticstics_languages[language] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": len(salaries_by_vacancy),
            "average_salary": average_salary,
        }
    title = '-SuperJob Moscow-'
    table_data = (
        ('Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'),
        *((language, value['vacancies_found'], value['vacancies_processed'], value['average_salary'])
          for language, value in staticstics_languages.items())
    )

    table = AsciiTable(table_data, title=title)
    return (table.table)



