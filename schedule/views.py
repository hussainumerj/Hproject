from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Meeting
from .forms import MeetingForm

@login_required
def schedule_home(request):
    now = timezone.now()
    upcoming = Meeting.objects.filter(date_time__gte=now).order_by('date_time')[:5]
    weekly   = Meeting.objects.filter(date_time__gte=now, date_time__lt=now + timedelta(days=7))
    monthly  = Meeting.objects.filter(date_time__gte=now, date_time__lt=now + timedelta(days=30))
    return render(request, 'schedule/schedule_home.html', {
        'upcoming': upcoming,
        'weekly': weekly,
        'monthly': monthly,
    })

@login_required
def schedule_create(request):
    form = MeetingForm(request.POST or None)
    if form.is_valid():
        meeting = form.save(commit=False)
        meeting.created_by = request.user
        meeting.save()
        return redirect('schedule_home')
    return render(request, 'schedule/schedule_form.html', {'form': form, 'action': 'Schedule'})

@login_required
def schedule_edit(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    form = MeetingForm(request.POST or None, instance=meeting)
    if form.is_valid():
        form.save()
        return redirect('schedule_home')
    return render(request, 'schedule/schedule_form.html', {'form': form, 'action': 'Edit'})

@login_required
def schedule_delete(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        meeting.delete()
        return redirect('schedule_home')
    return render(request, 'schedule/schedule_confirm_delete.html', {'meeting': meeting})