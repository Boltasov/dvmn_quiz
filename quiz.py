import random


def get_quiz():
    with open("quiz-questions/1vs1200.txt", "r", encoding="KOI8-R") as my_file:
        file_contents = my_file.read()

    quiz_parts = file_contents.split('\n\n')

    questions_and_answers = []
    pair = {}
    for part in quiz_parts:
        if r'Вопрос ' in part:
            pair['question'] = part.replace('\n', '')
            continue
        if 'Ответ:' in part:
            answer_text = part.split(':')[1].replace('\n', '')
            pair['answer'] = answer_text
            questions_and_answers.append(pair)
            pair = {}

    return questions_and_answers


def get_random_question():
    quiz = get_quiz()
    question_id = random.randint(0, len(quiz))
    question = quiz[question_id]['question']
    return question_id, question


def get_answer(question_id):
    quiz = get_quiz()
    answer = quiz[question_id]['answer']
    return answer

