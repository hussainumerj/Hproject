from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from organisation.models import Team, Dependency


@login_required
def dashboard(request):
    teams = Team.objects.all()
    recent_teams = Team.objects.all()[:3]

    team_count = teams.count()
    member_count = sum(team.members.count() for team in teams)
    repo_count = sum(1 for team in teams if team.code_repository)

    return render(request, "dashboard.html", {
        "recent_teams": recent_teams,
        "team_count": team_count,
        "member_count": member_count,
        "repo_count": repo_count,
    })


def signup(request):
    if request.user.is_authenticated:
        return redirect("team_list")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = UserCreationForm()

    return render(request, "registration/signup.html", {
        "form": form
    })


@login_required
def profile(request):
    success = False

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()

        if username:
            request.user.username = username
        request.user.email = email
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save()

        success = True

    return render(request, "registration/profile.html", {
        "success": success
    })


@login_required
def team_list(request):
    query = request.GET.get("q", "").strip()

    if query:
        teams = Team.objects.filter(
            Q(name__icontains=query) |
            Q(manager__username__icontains=query) |
            Q(department__name__icontains=query)
        ).distinct()
    else:
        teams = Team.objects.all()

    return render(request, "teams/team_list.html", {
        "teams": teams,
        "query": query,
    })


@login_required
def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    members = team.members.all()
    upstream_dependencies = Dependency.objects.filter(upstream_team=team)
    downstream_dependencies = Dependency.objects.filter(downstream_team=team)

    return render(request, "teams/team_detail.html", {
        "team": team,
        "members": members,
        "upstream_dependencies": upstream_dependencies,
        "downstream_dependencies": downstream_dependencies,
    })


@login_required
def email_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    success = False
    error = ""
    subject = ""
    message = ""

    if request.method == "POST":
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        if not team.email:
            error = "This team does not have an email address configured."
        elif not subject or not message:
            error = "Subject and message are required."
        else:
            try:
                sender_email = request.user.email if request.user.email else settings.DEFAULT_FROM_EMAIL

                full_message = (
                    f"Message sent from Sky Portal\n\n"
                    f"From user: {request.user.username}\n"
                    f"Sender email: {sender_email}\n"
                    f"Team: {team.name}\n\n"
                    f"{message}"
                )

                send_mail(
                    subject=subject,
                    message=full_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[team.email],
                    fail_silently=False,
                )

                success = True
                subject = ""
                message = ""

            except Exception:
                error = "The email could not be sent. Please try again."

    return render(request, "teams/email_team.html", {
        "team": team,
        "success": success,
        "error": error,
        "subject": subject,
        "message": message,
    })


@login_required
def schedule_meeting(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    members = team.members.all()

    success_message = None
    error = ""
    submitted_data = None

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        meeting_date = request.POST.get("meeting_date", "").strip()
        meeting_time = request.POST.get("meeting_time", "").strip()
        platform = request.POST.get("platform", "").strip()
        message = request.POST.get("message", "").strip()
        selected_members = request.POST.getlist("members")

        selected_member_objects = [
            member for member in members if str(member.id) in selected_members
        ]
        selected_usernames = [member.username for member in selected_member_objects]

        submitted_data = {
            "title": title,
            "meeting_date": meeting_date,
            "meeting_time": meeting_time,
            "platform": platform,
            "message": message,
            "selected_members": selected_members,
            "selected_usernames": selected_usernames,
        }

        if not title or not meeting_date or not meeting_time or not platform:
            error = "Please complete all required meeting fields."
        else:
            success_message = f"Meeting request for {team.name} submitted successfully."

    return render(request, "teams/schedule_meeting.html", {
        "team": team,
        "members": members,
        "success_message": success_message,
        "error": error,
        "submitted_data": submitted_data,
    })