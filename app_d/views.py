# myapp/views.py

from django.shortcuts import render
from django.http import HttpResponse
import PyPDF2
import json
import re

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render
import os
# views.py

# views.py
from django.shortcuts import render, redirect


def analyze_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)

        json_data = []
        current_question = None

        for page_number in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_number]
            text = page.extract_text()

            for line in text.split('\n'):
                if line.strip():
                    if line.strip()[0].isdigit():
                        if current_question:
                            json_data.append(current_question)

                        n = line.strip()
                        current_question = {'question': n, 'options': []}
                   
                    elif current_question and any(((char == ')' and char.isalpha() and ('а' <= char.lower() <= 'я' or 'a' <= char.lower() <= 'z' or 'ә' <= char.lower() <= 'ү' or 'і' == char.lower())) or char in {'(', ')','.',''} or ('А' <= char <= 'Я' or 'A' <= char <= 'Z' or 'Ә' <= char <= 'Ү' or 'І' == char)) for char in line):
                        current_question['options'].append(line.strip())
                    elif current_question and not current_question['options']:
                        current_question['question'] += ' ' + line.strip()
                    elif current_question and current_question['options']:
                        current_question['options'][len(current_question['options'])-1] += ' ' + line.strip()
        if current_question:
            json_data.append(current_question)

    return json_data

def save_to_json(json_data, output_file):
    # Получите полный путь к файлу в папке "json_files"
    output_path = os.path.join("pdfs", output_file)

    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)
def extract_answers_from_pdf(pdf_path):
    answers = {}

    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()

            # Разделение текста на строки
            lines = text.split('\n')

            for line in lines:
                # Разделение строки на номер вопроса и ответ
                parts = line.split('.')
                if len(parts) >= 2:
                    question_number = parts[0].strip()
                    answer = '.'.join(parts[1:]).strip()
                    answers[question_number] = answer

    return answers

def save_answers_to_json(answers, json_path):
    with open(json_path, 'w') as json_file:
        json.dump(answers, json_file, indent=4, ensure_ascii=False)
def pdf(request):
    if request.method == 'POST' and request.FILES['pdf_file_questions'] and request.FILES['pdf_file_answers']:
        pdf_file_questions = request.FILES['pdf_file_questions']
        pdf_file_answers = request.FILES['pdf_file_answers']

        # Укажите директорию 'pdfs' в методе save
        fs = FileSystemStorage(location='pdfs')

        # Сохранение файлов
        filename_questions = fs.save(pdf_file_questions.name, pdf_file_questions)
        filename_answers = fs.save(pdf_file_answers.name, pdf_file_answers)

        # Получение полного пути к сохраненным файлам
        saved_file_path_questions = os.path.join(fs.location, filename_questions)
        saved_file_path_answers = os.path.join(fs.location, filename_answers)

        # Ваш код для дополнительной обработки файлов, если необходимо
        data_questions = analyze_pdf(saved_file_path_questions)
        data_answers = extract_answers_from_pdf(saved_file_path_answers)

        # Сохранение данных в JSON-файлы
        output_json_file_questions = filename_questions + '.json'
        output_json_file_answers = 'pdfs/'+filename_answers + '_answers.json'

        save_to_json(data_questions, output_json_file_questions)
        save_answers_to_json(data_answers, output_json_file_answers)

        return HttpResponse(f'PDF files uploaded successfully! Path: {saved_file_path_questions}, {saved_file_path_answers}')

    return render(request, 'index.html')


