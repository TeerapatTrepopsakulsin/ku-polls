import datetime
import time

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from mysite import settings

from .models import Question, Choice, Vote


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


def create_question(question_text, pub_days=0, end_days=None, num_choice=0):
    """
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
    question = Question.objects.create(question_text=question_text, pub_date=pub_time, end_date=end_time)
    for i in range(num_choice):
        question.choice_set.create(choice_text=str(i))
    return question


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
        question = create_question(question_text="Past question.", pub_days=-30)
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
        create_question(question_text="Future question.", pub_days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", pub_days=-30)
        create_question(question_text="Future question.", pub_days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", pub_days=-30)
        question2 = create_question(question_text="Past question 2.", pub_days=-5)
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
        future_question = create_question(question_text="Future question.", pub_days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertRedirects(response, reverse("polls:index"))

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.", pub_days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_after_end_date_question(self):
        """
        The detail view of a question with an end_date in the past
        should redirect to polls index page.
        """
        after_end_date = create_question(question_text="Past Question.", pub_days=-10, end_days=-5)
        url = reverse("polls:detail", args=(after_end_date.id,))
        response = self.client.get(url)
        self.assertRedirects(response, reverse("polls:index"))

    def test_redirect_to_result_page_after_vote(self):
        """
        The detail view should redirect to result view when
        user vote.
        """
        question = create_question('question', num_choice=1)
        choice = question.choice_set.all()[0]
        vote_url = reverse("polls:vote", args=(question.id,))
        response = self.client.post(vote_url, {'choice': choice.id})
        self.assertEqual(response.status_code, 302)


class QuestionResultsViewTests(TestCase):
    def test_future_question(self):
        """
        The results view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future question.", pub_days=5)
        url = reverse("polls:results", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The results view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.", pub_days=-5)
        url = reverse("polls:results", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class UserAuthTest(TestCase):
    """Tests of user authentication."""
    def setUp(self):
        # superclass setUp creates a Client object and initializes test database
        super().setUp()
        self.username = "testuser"
        self.password = "FatChance!"
        self.user1 = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="testuser@nowhere.com"
        )
        self.user1.first_name = "Tester"
        self.user1.save()
        # we need a poll question to test voting
        q = Question.objects.create(question_text="First Poll Question")
        q.save()
        # a few choices
        for n in range(1, 4):
            choice = Choice(choice_text=f"Choice {n}", question=q)
            choice.save()
        self.question = q

    def vote(self, question: Question, choice: Choice):
        vote_url = reverse("polls:vote", args=(question.id,))
        response = self.client.post(vote_url, {'choice': choice.id})
        return response

    def test_logout(self):
        """A user can logout using the logout url.

        As an authenticated user,
        when I visit /accounts/logout/
        then I am logged out
        and then redirected to the login page.
        """
        logout_url = reverse("logout")
        # Authenticate the user.
        # We want to logout this user, so we need to associate the
        # user user with a session.  Setting client.user = ... doesn't work.
        # Use Client.login(username, password) to do that.
        # Client.login returns true on success
        self.assertTrue(
            self.client.login(username=self.username, password=self.password)
        )
        # visit the logout page
        form_data = {}
        response = self.client.post(logout_url, form_data)
        self.assertEqual(302, response.status_code)

        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))

    def test_login_view(self):
        """A user can login using the login view."""
        login_url = reverse("login")
        # Can get the login page
        response = self.client.get(login_url)
        self.assertEqual(200, response.status_code)
        # Can login using a POST request
        # usage: client.post(url, {'key1":"value", "key2":"value"})
        form_data = {"username": "testuser",
                     "password": "FatChance!"
                     }
        response = self.client.post(login_url, form_data)
        # after successful login, should redirect browser somewhere
        self.assertEqual(302, response.status_code)
        # should redirect us to the polls index page ("polls:index")
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

    def test_one_user_one_vote(self):
        """
        An authenticated user gets only 1 vote per poll.
        A user can change his vote on a poll during the voting period
        and his new vote replaces his old vote.
        """
        # User login
        user = self.user1
        self.client.force_login(user)

        # Create question
        question = create_question(question_text="question", num_choice=2)
        choice1 = question.choice_set.all()[0]
        choice2 = question.choice_set.all()[1]
        self.assertEqual(choice1.votes, 0)
        self.assertEqual(choice2.votes, 0)

        # Vote Choice1
        self.vote(question, choice1)
        self.assertEqual(choice1.votes, 1)
        self.assertEqual(choice2.votes, 0)

        # Vote Choice1 again
        self.vote(question, choice1)
        self.assertEqual(choice1.votes, 1)
        self.assertEqual(choice2.votes, 0)

        # Vote Choice2
        self.vote(question, choice2)
        self.assertEqual(choice1.votes, 0)
        self.assertEqual(choice2.votes, 1)
