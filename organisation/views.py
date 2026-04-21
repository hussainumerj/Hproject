from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Department, Team, TeamType, Dependency, AuditLog
from .forms import DepartmentForm, TeamForm, DependencyForm


# ─────────────────────────────────────────────
# ORGANISATION OVERVIEW
# ─────────────────────────────────────────────

@login_required
def organisation_overview(request):
    """Main organisation page showing all departments and team counts."""
    departments = Department.objects.prefetch_related('teams').all()
    total_teams = Team.objects.filter(status='active').count()
    total_departments = departments.count()

    context = {
        'departments': departments,
        'total_teams': total_teams,
        'total_departments': total_departments,
    }
    return render(request, 'organisation/overview.html', context)


# ─────────────────────────────────────────────
# DEPARTMENT VIEWS
# ─────────────────────────────────────────────

@login_required
def department_list(request):
    """List all departments with search support."""
    query = request.GET.get('q', '')
    departments = Department.objects.prefetch_related('teams').select_related('leader')

    if query:
        departments = departments.filter(
            Q(name__icontains=query) |
            Q(specialisation__icontains=query) |
            Q(leader__first_name__icontains=query) |
            Q(leader__last_name__icontains=query)
        )

    context = {
        'departments': departments,
        'query': query,
    }
    return render(request, 'organisation/department_list.html', context)


@login_required
def department_detail(request, pk):
    """View a single department and all its teams."""
    department = get_object_or_404(Department, pk=pk)
    teams = department.teams.select_related('manager', 'team_type').prefetch_related('members')

    context = {
        'department': department,
        'teams': teams,
    }
    return render(request, 'organisation/department_detail.html', context)


@login_required
def department_create(request):
    """Create a new department (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to create departments.')
        return redirect('organisation:department_list')

    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            AuditLog.objects.create(
                user=request.user,
                action='created',
                model_name='Department',
                object_id=department.pk,
                description=f'Department "{department.name}" created.'
            )
            messages.success(request, f'Department "{department.name}" created successfully.')
            return redirect('organisation:department_detail', pk=department.pk)
    else:
        form = DepartmentForm()

    return render(request, 'organisation/department_form.html', {'form': form, 'action': 'Create'})


@login_required
def department_edit(request, pk):
    """Edit an existing department (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit departments.')
        return redirect('organisation:department_list')

    department = get_object_or_404(Department, pk=pk)

    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            AuditLog.objects.create(
                user=request.user,
                action='updated',
                model_name='Department',
                object_id=department.pk,
                description=f'Department "{department.name}" updated.'
            )
            messages.success(request, f'Department "{department.name}" updated.')
            return redirect('organisation:department_detail', pk=department.pk)
    else:
        form = DepartmentForm(instance=department)

    return render(request, 'organisation/department_form.html', {'form': form, 'action': 'Edit'})


@login_required
def department_delete(request, pk):
    """Delete a department (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete departments.')
        return redirect('organisation:department_list')

    department = get_object_or_404(Department, pk=pk)

    if request.method == 'POST':
        name = department.name
        AuditLog.objects.create(
            user=request.user,
            action='deleted',
            model_name='Department',
            object_id=department.pk,
            description=f'Department "{name}" deleted.'
        )
        department.delete()
        messages.success(request, f'Department "{name}" deleted.')
        return redirect('organisation:department_list')

    return render(request, 'organisation/department_confirm_delete.html', {'department': department})


# ─────────────────────────────────────────────
# TEAM VIEWS
# ─────────────────────────────────────────────

@login_required
def team_list(request):
    """List all teams with search support."""
    query = request.GET.get('q', '')
    teams = Team.objects.select_related('department', 'manager', 'team_type').prefetch_related('members')

    if query:
        teams = teams.filter(
            Q(name__icontains=query) |
            Q(department__name__icontains=query) |
            Q(manager__first_name__icontains=query) |
            Q(manager__last_name__icontains=query)
        )

    context = {
        'teams': teams,
        'query': query,
    }
    return render(request, 'organisation/team_list.html', context)


@login_required
def team_detail(request, pk):
    """View a single team with full details."""
    team = get_object_or_404(
        Team.objects.select_related('department', 'manager', 'team_type').prefetch_related('members'),
        pk=pk
    )
    upstream = Dependency.objects.filter(upstream_team=team).select_related('downstream_team')
    downstream = Dependency.objects.filter(downstream_team=team).select_related('upstream_team')

    context = {
        'team': team,
        'upstream_dependencies': upstream,
        'downstream_dependencies': downstream,
    }
    return render(request, 'organisation/team_detail.html', context)


# ─────────────────────────────────────────────
# DEPENDENCY VIEWS
# ─────────────────────────────────────────────

@login_required
def dependency_map(request):
    """Show all team dependencies as a visual map."""
    teams = Team.objects.filter(status='active').select_related('department')
    dependencies = Dependency.objects.select_related('upstream_team', 'downstream_team')

    # Build JSON-friendly data for JS visualisation
    nodes = [{'id': t.pk, 'label': t.name, 'group': t.department.name if t.department else 'None'} for t in teams]
    edges = [{'from': d.upstream_team.pk, 'to': d.downstream_team.pk} for d in dependencies]

    context = {
        'teams': teams,
        'dependencies': dependencies,
        'nodes': nodes,
        'edges': edges,
    }
    return render(request, 'organisation/dependency_map.html', context)


@login_required
def dependency_create(request):
    """Create a dependency between two teams (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to manage dependencies.')
        return redirect('organisation:dependency_map')

    if request.method == 'POST':
        form = DependencyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dependency created successfully.')
            return redirect('organisation:dependency_map')
    else:
        form = DependencyForm()

    return render(request, 'organisation/dependency_form.html', {'form': form})


# ─────────────────────────────────────────────
# AUDIT LOG
# ─────────────────────────────────────────────

@login_required
def audit_log(request):
    """View audit trail of all changes (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('organisation:organisation_overview')

    logs = AuditLog.objects.select_related('user').order_by('-timestamp')
    return render(request, 'organisation/audit_log.html', {'logs': logs})
