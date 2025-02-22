from datetime import datetime
from flask import Blueprint, request, jsonify
from models.model import Subject, Chapter, Quiz, db, Question
from auth.protected_routes import token_required  # Import the token decorator


admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/subjects', methods=['POST'])
@token_required
def create_subject(current_user):
    if not current_user.is_admin:
        return jsonify({"message": "Admin access required."}), 403

    data = request.get_json()
    name = data.get('name')
    qualification = data.get('qualification')
    description = data.get("description")

    # Validate input
    if not name or not qualification:
        return jsonify({"message": "Name and qualification are required."}), 400
    if not (5 <= qualification <= 12):
        return jsonify({"message": "Qualification must be between 5 and 12."}), 400

    # Check if subject already exists
    existing_subject = Subject.query.filter_by(name=name, qualification=qualification).first()
    if existing_subject:
        return jsonify({"message": "Subject already exists for this qualification."}), 400

    # Create new subject
    new_subject = Subject(name=name, qualification=qualification, description=description)
    db.session.add(new_subject)
    db.session.commit()

    return jsonify({"message": "Subject created successfully.", "subject": {
        "id": new_subject.id,
        "name": new_subject.name,
        "qualification": new_subject.qualification,
        "description": new_subject.description
    }}), 201


@admin_bp.route('/subjects', methods=['GET'])
@token_required
def list_subjects(current_user):
    print(current_user.is_admin)
    if not current_user.is_admin:
        return jsonify({"message": "Admin access required."}), 403

    subjects = Subject.query.all()
    subject_list = [{
        "id": subject.id,
        "name": subject.name,
        "qualification": subject.qualification
    } for subject in subjects]

    return jsonify({"subjects": subject_list}), 200

@admin_bp.route('/subjects/<int:subject_id>', methods=['PUT'])
@token_required
def update_subject(current_user, subject_id):
    if not current_user.is_admin:
        return jsonify({"message": "Admin access required."}), 403

    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({"message": "Subject not found."}), 404

    data = request.get_json()
    subject.name = data.get('name', subject.name)
    subject.qualification = data.get('qualification', subject.qualification)

    db.session.commit()

    return jsonify({"message": "Subject updated successfully.", "subject": {
        "id": subject.id,
        "name": subject.name,
        "qualification": subject.qualification
    }}), 200

@admin_bp.route('/subjects/<int:subject_id>', methods=['DELETE'])
@token_required
def delete_subject(current_user, subject_id):
    if not current_user.is_admin:
        return jsonify({"message": "Admin access required."}), 403

    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({"message": "Subject not found."}), 404

    db.session.delete(subject)
    db.session.commit()

    return jsonify({"message": "Subject deleted successfully."}), 200



# chapters crud implementation-----------

@admin_bp.route('/chapters' , methods=['POST'])
@token_required
def create_chapter(current_user):
    if not current_user.is_admin:
        return jsonify({"message": "Admin access requires"}), 403
    
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    subject_id = data.get('subject_id')
    
    # Check if subject exists
    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({"message": "Subject not found."}), 404


    # validation of user input
    if not name or not description or not subject_id:
        return jsonify({"message": "All fields are required"}), 400
    
    # check if chapter already exists
    existing_chapter = Chapter.query.filter_by(name=name, subject_id=subject_id).first()
    if existing_chapter:
        return jsonify({"message": "Chapter already exists"}), 400

    # create new chapter
    new_chapter = Chapter(name=name, description=description, subject_id=subject_id)
    db.session.add(new_chapter)
    db.session.commit()

    return jsonify({"message": "Chapter created successfully", "chapter": {
        "id": new_chapter.id,
        "name": new_chapter.name,
        "description": new_chapter.description,
        "subject_id": new_chapter.subject_id
    }}), 201

@admin_bp.route('/chapters', methods=['GET'])
@token_required
def list_chapters(current_user):
    if not current_user.is_admin:
        return jsonify({"message": "Admin access required."}), 403

    chapters = Chapter.query.all()
    chapter_list = [{
        "id": chapter.id,
        "name": chapter.name,
        "description": chapter.description,
        "subject": {    
            "id": chapter.subject.id,
            "name": chapter.subject.name,
            "qualification": chapter.subject.qualification,
            "description": chapter.subject.description  
        }
    } for chapter in chapters]

    return jsonify({"chapters": chapter_list}), 200


@admin_bp.route('/chapters/<int:chapter_id>', methods=['PUT'])
@token_required
def update_chapter(current_user, chapter_id):
    if not current_user.is_admin:
        return jsonify({"message": "Admin access required."}), 403

    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        return jsonify({"message": "Chapter not found."}), 404

    data = request.get_json()
    chapter.name = data.get('name', chapter.name)
    chapter.description = data.get('description', chapter.description)

    
    # Update subject if provided
    new_subject_id = data.get('subject_id')
    if new_subject_id:
        subject = Subject.query.get(new_subject_id)
        if not subject:
            return jsonify({"message": "New subject not found."}), 404
        chapter.subject_id = new_subject_id

    db.session.commit()

    return jsonify({"message": "Chapter updated successfully.", "chapter": {
        "id": chapter.id,
        "name": chapter.name,
        "subject_id": chapter.subject_id
    }}), 200


@admin_bp.route('/chapters/<int:chapter_id>', methods=['DELETE'])
@token_required
def delete_chapter(current_user, chapter_id):
    if not current_user.is_admin:
        return jsonify({"message": "Admin access required."}), 403

    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        return jsonify({"message": "Chapter not found."}), 404

    db.session.delete(chapter)
    db.session.commit()

    return jsonify({"message": "Chapter deleted successfully."}), 200


# quiz crud implementation--------------
@admin_bp.route('/quizzes', methods=['POST'])
@token_required
def create_quiz(current_user):
    if not current_user.is_admin:
        return jsonify({"message": "Admin access required."}), 403

    data = request.get_json()
    chapter_id = data.get('chapter_id')
    date_of_quiz = data.get('date_of_quiz')
    time_duration = data.get('time_duration')
    remarks = data.get('remarks')

    # Validate input
    if not chapter_id or not date_of_quiz or not time_duration:
        return jsonify({"message": "chapter_id, date_of_quiz, and time_duration are required."}), 400

    # Check if chapter exists
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        return jsonify({"message": "Chapter not found."}), 404

    # Convert string date and time to proper format
    try:
        date_of_quiz = datetime.strptime(date_of_quiz, "%Y-%m-%d").date()
        time_duration = datetime.strptime(time_duration, "%H:%M").time()
    except ValueError:
        return jsonify({"message": "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time."}), 400

    # Create new quiz
    new_quiz = Quiz(
        chapter_id=chapter_id,
        date_of_quiz=date_of_quiz,
        time_duration=time_duration,
        remarks=remarks
    )
    db.session.add(new_quiz)
    db.session.commit()

    return jsonify({"message": "Quiz created successfully.", "quiz": {
        "id": new_quiz.id,
        "chapter_id": new_quiz.chapter_id,
        "date_of_quiz": str(new_quiz.date_of_quiz),
        "time_duration": str(new_quiz.time_duration),
        "remarks": new_quiz.remarks
    }}), 201


@admin_bp.route('/quizzes', methods=['GET'])
@token_required
def list_quizzes(current_user):
    if not current_user.is_admin:
        return jsonify({"message": "Admin access required."}), 403

    quizzes = Quiz.query.all()
    quiz_list = [{
        "id": quiz.id,
        "chapter_id": quiz.chapter_id,
        "date_of_quiz": str(quiz.date_of_quiz),
        "time_duration": str(quiz.time_duration),
        "remarks": quiz.remarks
    } for quiz in quizzes]

    return jsonify({"quizzes": quiz_list}), 200


@admin_bp.route('/quizzes/<int:quiz_id>', methods=['PUT'])
@token_required
def update_quiz(current_user, quiz_id):
    if not current_user.is_admin:
        return jsonify({"message": "Admin access required."}), 403

    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"message": "Quiz not found."}), 404

    data = request.get_json()

    # Update fields if provided
    if 'date_of_quiz' in data:
        try:
            quiz.date_of_quiz = datetime.strptime(data['date_of_quiz'], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"message": "Invalid date format. Use YYYY-MM-DD."}), 400

    if 'time_duration' in data:
        try:
            quiz.time_duration = datetime.strptime(data['time_duration'], "%H:%M").time()
        except ValueError:
            return jsonify({"message": "Invalid time format. Use HH:MM."}), 400

    if 'remarks' in data:
        quiz.remarks = data['remarks']

    if 'chapter_id' in data:
        chapter = Chapter.query.get(data['chapter_id'])
        if not chapter:
            return jsonify({"message": "New chapter not found."}), 404
        quiz.chapter_id = data['chapter_id']

    db.session.commit()

    return jsonify({"message": "Quiz updated successfully.", "quiz": {
        "id": quiz.id,
        "chapter_id": quiz.chapter_id,
        "date_of_quiz": str(quiz.date_of_quiz),
        "time_duration": str(quiz.time_duration),
        "remarks": quiz.remarks
    }}), 200


@admin_bp.route('/quizzes/<int:quiz_id>', methods=['DELETE'])
@token_required
def delete_quiz(current_user, quiz_id):
    if not current_user.is_admin:
        return jsonify({"message": "Admin access required."}), 403

    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"message": "Quiz not found."}), 404

    db.session.delete(quiz)
    db.session.commit()

    return jsonify({"message": "Quiz deleted successfully."}), 200




@admin_bp.route('/questions', methods=['POST'])
@token_required
def create_question(current_user):
    if not current_user.is_admin:
        return jsonify({"message": "Admin access required."}), 403

    data = request.json
    quiz_id = data.get('quiz_id')
    question_statement = data.get('question_statement')
    options = [data.get('option1'), data.get('option2'), data.get('option3'), data.get('option4')]
    correct_option = data.get('correct_option')

    if not all([quiz_id, question_statement, correct_option]) or None in options:
        return jsonify({"error": "Missing required fields"}), 400

    # Validate quiz exists
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404

    new_question = Question(
        quiz_id=quiz_id,
        question_statement=question_statement,
        option1=options[0],
        option2=options[1],
        option3=options[2],
        option4=options[3],
        correct_option=correct_option
    )
    
    db.session.add(new_question)
    db.session.commit()

    return jsonify({"message": "Question added successfully", "question_id": new_question.id}), 201


@admin_bp.route('/questions', methods=['GET'])
@token_required
def get_all_questions(current_user):
    questions = Question.query.all()
    
    question_list = [
        {
            "id": q.id,
            "quiz_id": q.quiz_id,
            "question_statement": q.question_statement,
            "options": [q.option1, q.option2, q.option3, q.option4],
            "correct_option": q.correct_option
        }
        for q in questions
    ]

    return jsonify({"questions": question_list}), 200



@admin_bp.route('/questions/<int:question_id>', methods=['GET'])
@token_required
def get_question_by_id(current_user, question_id):
    question = Question.query.get(question_id)
    
    if not question:
        return jsonify({"error": "Question not found"}), 404

    return jsonify({
        "id": question.id,
        "quiz_id": question.quiz_id,
        "question_statement": question.question_statement,
        "options": [question.option1, question.option2, question.option3, question.option4],
        "correct_option": question.correct_option
    }), 200


@admin_bp.route('/questions/<int:question_id>', methods=['PUT'])
@token_required
def update_question(current_user, question_id):
    if not current_user.is_admin:
        return jsonify({"message": "Admin access required."}), 403

    question = Question.query.get(question_id)
    if not question:
        return jsonify({"error": "Question not found"}), 404

    data = request.json
    question.question_statement = data.get('question_statement', question.question_statement)
    question.option1 = data.get('option1', question.option1)
    question.option2 = data.get('option2', question.option2)
    question.option3 = data.get('option3', question.option3)
    question.option4 = data.get('option4', question.option4)
    question.correct_option = data.get('correct_option', question.correct_option)

    db.session.commit()
    return jsonify({"message": "Question updated successfully"}), 200



@admin_bp.route('/questions/<int:question_id>', methods=['DELETE'])
@token_required
def delete_question(current_user, question_id):
    if not current_user.is_admin:
        return jsonify({"message": "Admin access required."}), 403

    question = Question.query.get(question_id)
    if not question:
        return jsonify({"error": "Question not found"}), 404

    db.session.delete(question)
    db.session.commit()
    
    return jsonify({"message": "Question deleted successfully"}), 200