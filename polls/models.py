"""The models module which contains elements in the polls app"""
import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    """
    A class used to represent a polls question within the app.
    Will contain different elements inside depends on the question type.
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField(verbose_name='date published',
                                    default=timezone.now)
    end_date = models.DateTimeField(verbose_name='ended date',
                                    blank=True, null=True)

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        """
        Check whether the question is published within a day
        :return: bool
        """
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """
        Check whether the current date-time is on or after
        question’s publication date.
        :return: bool
        """
        now = timezone.now()
        return self.pub_date <= now

    def can_vote(self):
        """
        Check whether the voting is allowed for this specific question.
        Voting is available when the current time
        is between the pub_date and end_date.
        If end_date is None, then can vote anytime after published.
        :return: bool
        """
        now = timezone.now()
        if self.end_date:
            return self.is_published() and now <= self.end_date
        return self.is_published()


class Choice(models.Model):
    """
    A class used to represent an individual choice in the polls question.
    Mostly used for a multiple choices polls question.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
