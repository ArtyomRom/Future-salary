from datetime import datetime, timedelta
from terminaltables import AsciiTable
from superjob import get_statistics_on_programming_languages_sj
import requests


def get_vacancies():
    today = datetime.today()
    text = 'программист'
    url = 'https://api.hh.ru/vacancies?text=программист&per_page=100&page=1'
    total_page = requests.get(url).json()['pages']
    vacancies = []
    for page in range(total_page):
        response = requests.get(f'https://api.hh.ru/vacancies?text={text}&per_page=100&page={page}').json()
        for vacancy in response['items']:
            created_at = datetime.strptime(vacancy['created_at'].split('T')[0], '%Y-%m-%d')
            if vacancy['area']['name'] == 'Москва' and today - created_at <= timedelta(days=30):
                vacancies.append(vacancy)
    return vacancies




def get_popular_languages(vacancies):
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

    for vacancy in vacancies:
        vacancy_text = (
            f"{vacancy['name']} {vacancy['snippet'].get('responsibility', '')} {vacancy['snippet'].get('requirement', '')}").lower()

        for language in popular_languages:
            if language.lower() in vacancy_text:
                popular_languages[language].append(vacancy)
            else:
                continue

    return popular_languages


def predict_rub_salary(vacancy):
    rub_salary = vacancy['salary']
    if rub_salary is not None and rub_salary['currency'] == "RUR" and isinstance(rub_salary['from'], int) and isinstance(
            rub_salary['to'], int):
        return (rub_salary['from'] * 1.2 + rub_salary['to'] * 0.8) / 2
    return None

def get_statistics_on_programming_languages():
    vacancies = get_vacancies()
    popular_languages = get_popular_languages(vacancies)
    languages = ['JavaScript', 'Python', 'Ruby', 'PHP', 'C++', 'C#', 'GO', 'Java', 'C']
    staticstics_languages = {}
    for language in languages:
        vacancies_found = len(popular_languages[language])
        if vacancies_found < 100:
            continue
        total_salary = [predict_rub_salary(vacancy) for vacancy in popular_languages[language] if isinstance(predict_rub_salary(vacancy), float)]
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