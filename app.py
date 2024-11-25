from flask import Flask, render_template, request
import os
import json
import csv

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_PATH = os.path.join(BASE_DIR, 'data', 'questions_with_weights.json')
RESULTS_PATH = os.path.join(BASE_DIR, 'data', 'results.csv')

with open(QUESTIONS_PATH, 'r', encoding='utf-8') as f:
    questions_data = json.load(f)

#csv에서 결과값 가져오는 함수
def load_results():
    results = {}
    with open(RESULTS_PATH, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            results[int(row['unique_code'])] = {
                "link": row["link"],
                "image": row["image"],
                "description": row["description"]
            }
    return results

results_data = load_results()

@app.route('/')
def index():
    """Render the first question."""
    first_question = "Q1: 용도"
    total_questions = len(questions_data)
    return render_template('index.html',
                           question=questions_data[first_question]['question'],
                           options=questions_data[first_question]['answers'],
                           current_question=first_question,
                           current_code=0,
                           progress=0,
                           total_questions=total_questions)

@app.route('/next_question', methods=['POST'])
def next_question():
    """Handle dynamic question flow and calculate unique code."""
    responses = request.form.to_dict()
    current_question = responses.get("current_question")
    selected_answer = responses.get("response")
    current_code = int(responses.get("current_code", 0))
    progress = int(responses.get("progress", 0))
    total_questions = int(responses.get("total_questions", 0))

    # 질문별 가중치계산
    weight = questions_data[current_question]["weight"]
    score = questions_data[current_question]["answers"][selected_answer]["score"]

    # 가중치로 고유번호 제작
    new_code = current_code + (score * weight)

    #진행상황프로그레스바
    next_question_key = questions_data[current_question]["answers"][selected_answer]["next"]
    progress += 1 

    if not next_question_key:  
        result = results_data.get(new_code, {"link": None, "image": None, "description": "결과 없음"})
        return render_template('result.html', unique_code=new_code, result=result)

    
    next_question = questions_data[next_question_key]
    return render_template('dynamic.html',
                           question=next_question['question'],
                           options=next_question['answers'],
                           current_question=next_question_key,
                           current_code=new_code,
                           progress=progress,
                           total_questions=total_questions)

if __name__ == '__main__':
    app.run(debug=True)
