"""Unittests for KU Polls views."""
import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from polls.models import Question


def create_question(question_text, pub_days=0, end_days=None, num_choice=0):
    """
    Create question object.

    Create a question with the given `question_text`, published the
    given number of `pub_days`, and ended the
    given number of `end_days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    The question contains `num_choice` amount of choices.
    """
    pub_time = timezone.now() + datetime.timedelta(days=pub_days)
    try:
        end_time = timezone.now() + datetime.timedelta(days=end_days)
    except TypeError:
        end_time = None
    question = Question.objects.create(question_text=question_text,
                                       pub_date=pub_time, end_date=end_time)
    for i in range(num_choice):
        question.choice_set.create(choice_text=str(i))
    return question


class QuestionIndexViewTests(TestCase):
    """Tests of index page view."""

    def test_no_questions(self):
        """If no questions exist, an appropriate message is displayed."""
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """Questions with a pub_date in the past are displayed on the index page."""
        question = create_question(question_text="Past question.",
                                   pub_days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self):
        """Questions with a pub_date in the future aren't displayed on the index page."""
        create_question(question_text="Future question.", pub_days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """Even if both past and future questions exist, only past questions are displayed."""
        question = create_question(question_text="Past question.",
                                   pub_days=-30)
        create_question(question_text="Future question.", pub_days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """The questions index page may display multiple questions."""
        question1 = create_question(question_text="Past question 1.",
                                    pub_days=-30)
        question2 = create_question(question_text="Past question 2.",
                                    pub_days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):
    """Tests of detail page view."""

    def test_future_question(self):
        """
        Tests detail page response for future question.

        The detail view of a question with a pub_date in the future
        should redirect to polls index page.
        """
        future_question = create_question(question_text="Future question.",
                                          pub_days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("polls:index"))

    def test_after_end_date_question(self):
        """
        Tests detail page response for question that pass end_date.

        The detail view of a question with an end_date in the past
        should redirect to polls index page.
        """
        after_end_date = create_question(question_text="Past Question.",
                                         pub_days=-10, end_days=-5)
        url = reverse("polls:detail", args=(after_end_date.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("polls:index"))

    def test_redirect_to_result_page_after_vote(self):
        """
        Tests detail page response after user has voted.

        The detail view should get redirect status code when user vote.
        """
        question = create_question('question', num_choice=1)
        choice = question.choice_set.all()[0]
        vote_url = reverse("polls:vote", args=(question.id,))
        response = self.client.post(vote_url, {'choice': choice.id})
        self.assertEqual(response.status_code, 302)


class QuestionResultsViewTests(TestCase):
    """Tests of result page view."""

    def test_future_question(self):
        """
        Tests result page response for future question.

        The results view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future question.",
                                          pub_days=5)
        url = reverse("polls:results", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        Tests result page response for past question.

        The results view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.",
                                        pub_days=-5)
        url = reverse("polls:results", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
