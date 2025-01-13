from datetime import datetime, timedelta

import requests
from terminaltables import AsciiTable

from superjob import get_statistics_on_programming_languages_sj


def get_popular_languages():
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
        popular_languages[language] = get_vacancies_by_language(language)

    return popular_languages


def get_vacancies_by_language(language: str):
    today = datetime.today()
    text = 'программист'
    params = {'text': f"{text} {language}", 'per_page': 100, 'page': 1, 'area': 1}
    url = 'https://api.hh.ru/vacancies/'
    vacancies = []
    while True:
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            response = response.json()
            for vacancy in response['items']:
                created_at = datetime.strptime(vacancy['created_at'].split('T')[0], '%Y-%m-%d')
                if today - created_at <= timedelta(days=30):
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
    rub_salary = vacancy['salary']
    if rub_salary is not None and rub_salary['currency'] == "RUR" and isinstance(rub_salary['from'],
                                                                                 int) and isinstance(
            rub_salary['to'], int):
        return (rub_salary['from'] * 1.2 + rub_salary['to'] * 0.8) / 2
    return None


def get_statistics_on_programming_languages():
    popular_languages = get_popular_languages()
    staticstics_languages = {}
    for language in popular_languages.keys():
        vacancies_found = len(popular_languages[language])
        if vacancies_found < 100:
            continue
        total_salary = [predict_rub_salary(vacancy) for vacancy in popular_languages[language] if
                        isinstance(vacancy['salary'], float|int)]
        average_salary = sum(total_salary) / len(total_salary) if len(total_salary) != 0 else "Нет данных о зарплате"
        staticstics_languages[language] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": len(total_salary),
            "average_salary": int(average_salary) if isinstance(average_salary, float) else average_salary,
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
    get_statistics_on_programming_languages()
    get_statistics_on_programming_languages_sj()
