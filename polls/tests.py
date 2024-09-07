import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
#
# from .models import Question


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_is_published_with_future_question(self):
        """
        is_published() returns False for questions whose pub_date
        is after the current time.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.is_published(), False)

    def test_is_published_with_default_question(self):
        """
        is_published() returns True for questions whose pub_date
        is at the current time (now).
        """
        now_question = Question()
        self.assertIs(now_question.is_published(), True)

    def test_is_published_with_old_question(self):
        """
        is_published() returns True for questions whose pub_date
        is before the current time.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.is_published(), True)

    def test_can_vote_with_default_end_date(self):
        """
        For null ended date, voting is allowed anytime after pub_date
        can_vote() returns True for questions whose pub_date
        is before the current time.
        """
        past = timezone.now() - datetime.timedelta(days=10)
        future = timezone.now() + datetime.timedelta(days=10)
        old_question = Question(pub_date=past)
        now_question = Question()
        future_question = Question(pub_date=future)
        self.assertIs(old_question.is_published(), True)
        self.assertIs(now_question.is_published(), True)
        self.assertIs(future_question.is_published(), False)

    def test_cannot_vote_after_end_date(self):
        """Cannot vote if the end_date is in the past."""
        end_date = timezone.now() - datetime.timedelta(seconds=1)
        pass_end_date_question = Question(end_date=end_date)
        self.assertIs(pass_end_date_question.can_vote(), False)

    def test_can_vote_before_the_end_date(self):
        """Can vote if the end_date is in the future."""
        end_date = timezone.now() + datetime.timedelta(seconds=1)
        before_end_date_question = Question(end_date=end_date)
        self.assertIs(before_end_date_question.can_vote(), True)

    def test_can_vote_at_the_end_date(self):
        """Can vote if the end_date is at the current time."""
        end_date = timezone.now()
        at_end_date_question = Question(end_date=end_date)
        self.assertIs(at_end_date_question.can_vote(), True)


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


def create_question_with_end_date(question_text, pub_days, end_days):
    """
    Create a question with the given `question_text`, published the
    given number of `pub_days`, and ended the
    given number of `end_days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    pub_time = timezone.now() + datetime.timedelta(days=pub_days)
    end_time = timezone.now() + datetime.timedelta(days=end_days)
    return Question.objects.create(question_text=question_text, pub_date=pub_time, end_date=end_time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        should redirect to polls index page.
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertRedirects(response, reverse("polls:index"))

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_after_end_date_question(self):
        """
        The detail view of a question with an end_date in the past
        should redirect to polls index page.
        """
        after_end_date = create_question_with_end_date(question_text="Past Question.", pub_days=-10, end_days=-5)
        url = reverse("polls:detail", args=(after_end_date.id,))
        response = self.client.get(url)
        self.assertRedirects(response, reverse("polls:index"))


class QuestionResultsViewTests(TestCase):
    def test_future_question(self):
        """
        The results view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("polls:results", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The results view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("polls:results", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
