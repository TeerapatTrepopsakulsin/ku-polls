"""KU Polls app UI."""
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import (user_logged_in,
                                         user_logged_out, user_login_failed)
from django.dispatch import receiver

from .models import Choice, Question, Vote

import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Get the visitor’s IP address using request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    """Log a message when user logging in to the app."""
    ip = request.META.get('REMOTE_ADDR')

    logger.info('login user: {user} via ip: {ip}'.format(
        user=user,
        ip=ip
    ))


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    """Log a message when user logging out of the app."""
    ip = request.META.get('REMOTE_ADDR')

    logger.info('logout user: {user} via ip: {ip}'.format(
        user=user,
        ip=ip
    ))


@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, **kwargs):
    """Log a message when user fail to logging in to the app."""
    logger.warning('login failed for: {credentials}'.format(
        credentials=credentials,
    ))


class IndexView(generic.ListView):
    """Display the list of the available polls to vote."""

    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the published questions."""
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cur_user = self.request.user
        latest_question_list = context["latest_question_list"]
        for question in latest_question_list:
            question.user_voted = question.cur_user_voted(cur_user)
            question.user_choice = question.cur_user_choice(cur_user)
        return context


class DetailView(generic.DetailView):
    """Display the choices of the polls to vote."""

    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """Excludes any questions that aren't published yet."""
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get_context_data(self, **kwargs):
        """Get user current vote choice into the context."""
        context = super().get_context_data(**kwargs)
        question = self.get_object()
        cur_user = self.request.user
        try:
            cur_vote = Vote.objects.get(user=cur_user,
                                        choice__question=question)
        except Vote.DoesNotExist:
            context['cur_choice'] = None
        else:
            context['cur_choice'] = cur_vote.choice
        return context

    def get(self, request, *args, **kwargs):
        """Render the poll detail page."""
        if self.request.user.is_authenticated:
            try:
                question = Question.objects.get(pk=self.kwargs['pk'])
            except Question.DoesNotExist:
                messages.error(request, 'The poll does not exist.')
                return redirect('polls:index')
            if question.can_vote():
                try:
                    current_user = request.user
                    vote = Vote.objects.get(user=current_user,
                                            choice__question=question)
                except Vote.DoesNotExist:
                    pass
                else:
                    messages.info(request=request,
                                  message=f"Your current choice is '{vote.choice}'")
                finally:
                    return super().get(request, *args, **kwargs)
            messages.error(request, 'Voting is not available for the poll.')
        else:
            messages.error(request, 'Please log in first!')
        return redirect('polls:index')


class ResultsView(generic.DetailView):
    """Display the vote result of the particular polls."""

    model = Question
    template_name = "polls/results.html"

    def get_queryset(self):
        """Excludes any questions that aren't published yet."""
        return Question.objects.filter(pub_date__lte=timezone.now())


@login_required
def vote(request, question_id):
    """
    Vote function for authenticated user.

    When user vote for a choice, save the new Vote objects into the database.
    Then, redirect user to the result page.
    """
    question = get_object_or_404(Question, pk=question_id)

    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        messages.error(request=request, message="You didn't select a choice.")
        return redirect("polls:detail", pk=question_id)

    current_user = request.user

    try:
        vote = Vote.objects.get(user=current_user, choice__question=question)
        # user have vote for this question
        vote.choice = selected_choice
        vote.save()
        messages.success(request=request,
                         message=f"Your vote are now '{selected_choice.choice_text}'")
    except Vote.DoesNotExist:
        vote = Vote.objects.create(user=current_user, choice=selected_choice)
        messages.success(request=request,
                         message=f"Your vote are now '{selected_choice.choice_text}'")

    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    logger.info(f'user:{current_user.username} '
                f'vote for choice:{selected_choice.id} '
                f'in question:{selected_choice.question.id}')
    return HttpResponseRedirect(reverse("polls:results",
                                        args=(question.id,)))


@login_required
def clear(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    current_user = request.user

    try:
        vote = Vote.objects.get(user=current_user, choice__question=question)
        # user have vote for this question
        vote.delete()
        messages.success(request=request,
                         message=f"Your vote has been cleared.")

        logger.info(f'user:{current_user.username} '
                    f'clear vote for choice:{vote.choice.id} '
                    f'in question:{question.id}')
    except Vote.DoesNotExist:
        messages.error(request=request, message=f"You haven't vote.")

    return HttpResponseRedirect(reverse("polls:detail",
                                        args=(question.id,)))
