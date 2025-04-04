import pytest
from model import Question, Choice


def test_create_question():
    question = Question(title='q1')
    assert question.id != None

def test_create_multiple_questions():
    question1 = Question(title='q1')
    question2 = Question(title='q2')
    assert question1.id != question2.id

def test_create_question_with_invalid_title():
    with pytest.raises(Exception):
        Question(title='')
    with pytest.raises(Exception):
        Question(title='a'*201)
    with pytest.raises(Exception):
        Question(title='a'*500)

def test_create_question_with_valid_points():
    question = Question(title='q1', points=1)
    assert question.points == 1
    question = Question(title='q1', points=100)
    assert question.points == 100

def test_create_choice():
    question = Question(title='q1')
    
    question.add_choice('a', False)

    choice = question.choices[0]
    assert len(question.choices) == 1
    assert choice.text == 'a'
    assert not choice.is_correct


def test_add_multiple_choices():
    question = Question(title='What is the capital of France?')
    question.add_choice('Paris', True)
    question.add_choice('London', False)
    question.add_choice('Berlin', False)
    
    assert len(question.choices) == 3
    assert question.choices[0].text == 'Paris'
    assert question.choices[0].is_correct == True

def test_remove_choice_by_id():
    question = Question(title='Pick a color')
    choice1 = question.add_choice('Red', False)
    _ = question.add_choice('Blue', True)
    
    assert len(question.choices) == 2
    question.remove_choice_by_id(choice1.id)
    assert len(question.choices) == 1
    assert question.choices[0].text == 'Blue'

def test_remove_all_choices():
    question = Question(title='Select a fruit')
    question.add_choice('Apple', True)
    question.add_choice('Banana', False)
    question.add_choice('Orange', False)
    
    assert len(question.choices) == 3
    question.remove_all_choices()
    assert len(question.choices) == 0

def test_set_correct_choices():
    question = Question(title='Select programming languages', max_selections=2)
    choice1 = question.add_choice('Python', False)
    _ = question.add_choice('JavaScript', False)
    choice3 = question.add_choice('Java', False)
    
    question.set_correct_choices([choice1.id, choice3.id])
    
    assert question.choices[0].is_correct == True
    assert question.choices[1].is_correct == False
    assert question.choices[2].is_correct == True


def test_can_select_within_max_limit():
    question = Question(title='Pick two colors', max_selections=2)
    red = question.add_choice('Red', True)
    blue = question.add_choice('Blue', False)
    green = question.add_choice('Green', True)

    selected_ids = question.select_choices([red.id, green.id])

    assert len(selected_ids) == 2
    assert red.id in selected_ids
    assert green.id in selected_ids

def test_raises_when_selection_exceeds_max_limit():
    question = Question(title='Pick one number', max_selections=1)
    one = question.add_choice('One', True)
    two = question.add_choice('Two', False)
    three = question.add_choice('Three', True)

    with pytest.raises(Exception) as exc:
        question.select_choices([one.id, three.id])
    
    assert "Cannot select more than 1 choices" in str(exc.value)

def test_removing_invalid_choice_raises_exception():
    question = Question(title='Pick a continent')
    europe = question.add_choice('Europe', True)

    with pytest.raises(Exception) as exc:
        question.remove_choice_by_id(999) 

    assert "Invalid choice id" in str(exc.value)

def test_choice_text_validation():
    with pytest.raises(Exception) as exc:
        Choice(id=1, text='')

    assert "Text cannot be empty" in str(exc.value)

    with pytest.raises(Exception) as exc:
        Choice(id=1, text='x' * 101)

    assert "Text cannot be longer than 100 characters" in str(exc.value)

def test_question_points_must_be_valid():
    with pytest.raises(Exception) as exc:
        Question(title='Invalid points low', points=0)

    assert "Points must be between 1 and 100" in str(exc.value)

    with pytest.raises(Exception) as exc:
        Question(title='Invalid points high', points=101)

    assert "Points must be between 1 and 100" in str(exc.value)

def test_only_correct_choices_are_selected():
    question = Question(title='Select animals that can fly', max_selections=3)
    eagle = question.add_choice('Eagle', True)
    penguin = question.add_choice('Penguin', False)
    bat = question.add_choice('Bat', True)

    selected_ids = question.select_choices([eagle.id, penguin.id, bat.id])

    assert len(selected_ids) == 2
    assert eagle.id in selected_ids
    assert penguin.id not in selected_ids
    assert bat.id in selected_ids

@pytest.fixture
def europe_question():
    question = Question(title="Which countries are in Europe?", points=5, max_selections=3)
    question.add_choice("France", True)
    question.add_choice("Japan", False)
    question.add_choice("Italy", True)
    question.add_choice("Brazil", False)
    return question

@pytest.fixture
def capital_question():
    question = Question(title="What is the capital of France?", points=2)
    question.add_choice("Paris", True)
    question.add_choice("London", False)
    question.add_choice("Berlin", False)
    return question

def test_counts_correct_choices(europe_question):
    correct = [c for c in europe_question.choices if c.is_correct]
    
    assert len(correct) == 2
    assert correct[0].text == "France"
    assert correct[1].text == "Italy"

def test_selecting_all_correct_choices(europe_question):
    correct_ids = [c.id for c in europe_question.choices if c.is_correct]
    selected_ids = europe_question.select_choices(correct_ids)

    assert len(selected_ids) == 2
    assert set(selected_ids) == set(correct_ids)

def test_selecting_mixed_choices_returns_only_correct(europe_question):
    selected_ids = europe_question.select_choices([
        europe_question.choices[0].id,
        europe_question.choices[1].id,
        europe_question.choices[2].id
    ])
    correct_ids = [c.id for c in europe_question.choices if c.is_correct]

    assert set(selected_ids).issubset(set(correct_ids))
    assert len(selected_ids) == 2
    assert europe_question.choices[1].id not in selected_ids

def test_single_choice_limit_enforced(capital_question):
    selected_ids = [c.id for c in capital_question.choices[:2]]

    with pytest.raises(Exception) as exc:
        capital_question.select_choices(selected_ids)

    assert "Cannot select more than 1 choices" in str(exc.value)

def test_choice_ids_are_sequential(capital_question):
    for index, choice in enumerate(capital_question.choices):
        assert choice.id == index + 1