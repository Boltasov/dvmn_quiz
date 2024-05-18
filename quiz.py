import random
import os


def get_quiz(quiz_file=''):
    abs_path = os.path.abspath('')
    print(abs_path)
    quiz_directory = os.path.join(abs_path, 'quiz-questions')
    print(quiz_directory)

    if len(quiz_file) < 1:
        quiz_file = random.choice(os.listdir(quiz_directory))

    quiz_path = os.path.join(quiz_directory, quiz_file)
    with open(quiz_path, 'r', encoding='KOI8-R') as my_file:
        file_contents = my_file.read()

    quiz_parts = file_contents.split('\n\n')

    questions_and_answers = []
    pair = {}
    for part in quiz_parts:
        if r'Вопрос ' in part:
            pair['question'] = part.replace('\n', ' ')
            continue
        if 'Ответ:' in part:
            answer_text = part.split(':')[1].replace('\n', ' ')
            pair['answer'] = answer_text
            questions_and_answers.append(pair)
            pair = {}

    return questions_and_answers, quiz_file


def get_random_question(quiz_file=''):
    quiz, quiz_file = get_quiz(quiz_file)
    question_id = random.randint(0, len(quiz))
    print(quiz[0])
    question = quiz[question_id]['question']
    return question_id, question, quiz_file


def get_answer(question_id, quiz_file):
    quiz, _ = get_quiz(quiz_file)
    answer = quiz[question_id]['answer']
    return answer

