"""Unittests for question model."""
import datetime

from django.test import TestCase
from django.utils import timezone

from polls.models import Question


class QuestionModelTests(TestCase):
    """Tests of question model."""

    def test_was_published_recently_with_future_question(self):
        """
        Tests was_published_recently() function with future question.

        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        Tests was_published_recently() function with old question.

        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        Tests was_published_recently() function with recent question.

        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = (timezone.now() -
                datetime.timedelta(hours=23, minutes=59, seconds=59))
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_is_published_with_future_question(self):
        """
        Tests is_published() function with future question.

        is_published() returns False for questions whose pub_date
        is after the current time.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.is_published(), False)

    def test_is_published_with_default_question(self):
        """
        Tests is_published() function with default question.

        is_published() returns True for questions whose pub_date
        is at the current time (now).
        """
        now_question = Question()
        self.assertIs(now_question.is_published(), True)

    def test_is_published_with_old_question(self):
        """
        Tests is_published() function with old question.

        is_published() returns True for questions whose pub_date
        is before the current time.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.is_published(), True)

    def test_can_vote_with_default_end_date(self):
        """
        For null ended date, voting is allowed anytime after pub_date.

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
