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

# exams/views.py
from django.shortcuts import render, get_object_or_404
from .models import Subject, QuestionAnswer
from django.http import HttpResponse
# exams/views.py
from django.shortcuts import render, redirect
from .models import Subject
from django.http import HttpResponse
from .forms import SubjectForm
from django.shortcuts import render
from .models import QuestionAnswer
import json

# Ваш вид solve_test
# Ваш вид solve_test
# Ваш вид solve_test
def solve_test(request, qa_id):
    question_answer = QuestionAnswer.objects.get(pk=qa_id)
    
    # Загрузка вопросов и ответов из JSON
    questions = json.loads(question_answer.questions_json)
       
    correct_answers = json.loads(question_answer.answers_json)

    if request.method == 'POST':
        # Обработка отправленных ответов
        user_answers = [request.POST.get(f"question_{question_id}") for question_id in range(1, len(questions) + 1)]
        user_answers = [i[0].lower() for i in user_answers]
        
        for i in (user_answers):
            print(ord(i))
        for i in correct_answers.values():
            print(ord(i))
        
        # Подсчет баллов
        score = sum([1 for user_answer, correct_answer in zip(user_answers, correct_answers.values()) if user_answer == correct_answer.lower()])
        
        return render(request, 'exams/test_result.html', {'score': score, 'total_questions': len(questions)})

    return render(request, 'exams/solve_test.html', {'questions': questions})

def add_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = SubjectForm()

    return render(request, 'exams/add_subject.html', {'form': form})

def index(request):
    subjects = Subject.objects.all()
    return render(request, 'exams/index.html', {'subjects': subjects})

def exam_detail(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    question_answers = QuestionAnswer.objects.filter(subject=subject)
    return render(request, 'exams/exam_detail.html', {'subject': subject, 'question_answers': question_answers})


def upload_test(request, subject_id):
    # Добавьте здесь код для обработки загрузки теста
    if request.method == 'POST' and request.FILES['test_file']:
        test_file = request.FILES['test_file']
        # Обработка файла
        return HttpResponse("Test uploaded successfully")
    return HttpResponse("Failed to upload test")
import os
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render
from .models import Subject, QuestionAnswer

def upload_test(request, subject_id):
    if request.method == 'POST' and request.FILES['tests_file'] and request.FILES['answers_file']:
        pdf_file_questions = request.FILES['tests_file']
        pdf_file_answers = request.FILES['answers_file']
 
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
        
        # Сохранение данных в базу данных
        subject = Subject.objects.get(pk=subject_id)

        # Создание объекта QuestionAnswer с использованием модели
        question_answer = QuestionAnswer.objects.create(
            subject=subject,
            questions_json=json.dumps(data_questions),
            answers_json=json.dumps(data_answers)
        )
        return HttpResponse(f'PDF files uploaded successfully! Path: {saved_file_path_questions}, {saved_file_path_answers}')

    return render(request, 'index.html')


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


