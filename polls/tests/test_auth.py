"""Unittests for authenticated user behavior."""
import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from mysite import settings

from polls.models import Question, Choice


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


class UserAuthTest(TestCase):
    """Tests of user authentication."""

    def setUp(self):
        """Set up the elements for authentication."""
        # superclass setUp creates a Client object
        # and initializes test database
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
        """Return user response of voting choice in the question."""
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

    def test_user_get_detail_question(self):
        """
        Tests user get detail page response for question.

        The detail view of a question with a pub_date in the past
        displays the question's text if user is authenticated.
        """
        # User login
        user = self.user1
        self.client.force_login(user)

        # Create question
        past_question = create_question(question_text="Past Question.")

        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, past_question.question_text)

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
