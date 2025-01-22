from datetime import datetime, timedelta
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


def get_vacancies_sj(languange: str, secret_key):
    vacancies_sj = []
    headers = {'X-Api-App-Id': secret_key}
    date_from = int((datetime.now() - timedelta(days=30)).timestamp())
    categoria_id = 48
    quantity_per_page = 40
    page = 0
    while True:
        try:
            params = {'keywords': languange, 'catalogues': categoria_id, 'town': 'Москва', 'page': page,
                      'count': quantity_per_page,
                      'date_published[from]': date_from}
            response = requests.get(f'https://api.superjob.ru/2.0/vacancies/', headers=headers, params=params)
            response.raise_for_status()
            response = response.json()
            for vacancy in response['objects']:
                vacancy['total'] = response['total']
                vacancies_sj.append(vacancy)

            if not response.get('more', False):
                break
            page += 1
        except requests.exceptions.RequestException as e:
            print(f"Произошла ошибка при запросе: {e}")
            break

    return vacancies_sj
def predict_rub_salary(vacancy, salary_from, salary_to):
    if vacancy['currency'] not in ('RUR', 'rub'):
        return None
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_from:
        return salary_from * 1.2
    elif salary_to:
        return salary_to * 0.8


def get_statistics_on_programming_languages_sj(secret_key: str):
    vacancies_by_language = group_vacancies_by_language_sj(secret_key)
    staticstics_languages = {}
    for language, vacancies in vacancies_by_language.items():
        vacancies_found = set(map(lambda vacancy: vacancy['total'], vacancies))
        if not vacancies_found:
            continue
        salaries_by_vacancy = [
            predict_rub_salary(vacancy, vacancy['payment_from'], vacancy['payment_to']) for vacancy
            in vacancies]
        salaries_by_vacancy = [salary for salary in salaries_by_vacancy if salary]
        average_salary = sum(salaries_by_vacancy) / len(salaries_by_vacancy) if salaries_by_vacancy else 0
        staticstics_languages[language] = {
            "vacancies_found": min(vacancies_found),
            "vacancies_processed": len(salaries_by_vacancy),
            "average_salary": average_salary,
        }
    return staticstics_languages

