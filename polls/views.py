from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
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
    ip = request.META.get('REMOTE_ADDR')

    logger.info('login user: {user} via ip: {ip}'.format(
        user=user,
        ip=ip
    ))


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')

    logger.info('logout user: {user} via ip: {ip}'.format(
        user=user,
        ip=ip
    ))


@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, **kwargs):
    logger.warning('login failed for: {credentials}'.format(
        credentials=credentials,
    ))


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    """Display the choices of the polls to vote."""
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    @staticmethod
    def render(request, pk, *args, **kwargs):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            messages.error(request, 'The poll does not exist.')
            return redirect('polls:index')
        if question.can_vote():
            try:
                current_user = request.user
                vote = Vote.objects.get(user=current_user, choice__question=question)
            except Vote.DoesNotExist:
                pass
            else:
                messages.info(request=request, message=f"Your current choice is '{vote.choice}'")
            finally:
                return render(request, "polls/detail.html",
                              {"question": question})
        messages.error(request, 'Voting is not available for the poll.')
        return redirect('polls:index')


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


@login_required
def vote(request, question_id):
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
        # vote = current_user.vote_set.get(choice__question=question)
        # user have vote for this question
        vote.choice = selected_choice
        vote.save()
        messages.success(request=request, message=f"Your vote are now '{selected_choice.choice_text}'")
    except Vote.DoesNotExist:
        vote = Vote.objects.create(user=current_user, choice=selected_choice)
        messages.success(request=request, message=f"Your vote are now '{selected_choice.choice_text}'")

    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    logger.info(f'user:{current_user.username} vote for choice:{selected_choice.id} in question:{selected_choice.question.id}')
    return HttpResponseRedirect(reverse("polls:results",
                                        args=(question.id,)))
