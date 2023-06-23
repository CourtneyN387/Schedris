# pylint: disable=no-member

from datetime import datetime
import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic.edit import CreateView, DeleteView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.decorators import method_decorator
from django.urls import reverse, reverse_lazy
from django.views import generic
from .models import Course, ShoppingCart, Schedule, addJsonCourse, ApprovalStatus
from .decorators import advisor_required, student_required

User = get_user_model()

# ------- Method-Based views for simple things ------
def home(request):
    """
    home view that allows you to access either the advisor index
    or the student index
    """

    return render(request, 'common/home.html')

def FAQ(request):
    """
    FAQ view that show the FAQ page
    """

    return render(request, 'common/FAQ.html')

def About(request):
    """
    About view that show the About page
    """

    return render(request, 'common/about.html')

@login_required
def course_list(request):
    # Make a GET request to the SIS API endpoint to retrieve the course data
    courses = []

    if request.method == 'GET' and request.GET:

        term = request.GET.get('Term')
        keyword = request.GET.get('keyword')
        subject = request.GET.get('subject')
        catalog = request.GET.get('catalog')
        department = request.GET.get('department')
        instruct = request.GET.get('instruct_modes')
        session_code = request.GET.get('session_code')
        location = request.GET.get('location')

        if not (keyword or subject or catalog or department):
            messages.error(request, 'Please fill one of the required fields (*) before searching.')
            return render(request, 'common/course_list.html')

        page = 1
            
        while page < 8:
            api_url = f'https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01&term={term}&subject={subject}&acad_org={department}&catalog_nbr={catalog}&instruction_mode={instruct}&keyword={keyword}&session_code={session_code}&location={location}&page={page}'
            response = requests.get(api_url)
            
            if response.status_code == 200:
                course_data = response.json()
            else:
                course_data = []

            for course in course_data: 
                # Process start_time
                if course['meetings']:
                    start_str = course['meetings'][0]['start_time']
                    if start_str:
                        start_str = start_str[:-6]
                        start_obj = datetime.strptime(start_str, '%H.%M.%S.%f')
                        start_readable = start_obj.strftime('%I:%M %p')
                        course['meetings'][0]['start_time'] = start_readable
                    else:
                        start_readable = 'No start time available'

                    # Process end_time
                    end_str = course['meetings'][0]['end_time']
                    if end_str:
                        end_str = end_str[:-6]
                        end_obj = datetime.strptime(end_str, '%H.%M.%S.%f')
                        end_readable = end_obj.strftime('%I:%M %p')
                        course['meetings'][0]['end_time'] = end_readable
                    else:
                        end_readable = 'No start time available'

                    # Add course to user's schedules
                addJsonCourse(course)

                # Append course to the courses list
                courses.append(course)

            courses.extend(course_data)
            page += 1

    schedules = Schedule.objects.filter(student=request.user)

    return render(request, 'common/course_list.html', {'courses': courses, 'schedules':schedules})


@login_required
@student_required
def shopping_cart(request):
    strm = request.GET.get('strm')
    if strm: 
        cart = ShoppingCart.objects.filter(user=request.user, strm=int(strm)).first()
    else: 
        cart = ShoppingCart.objects.first()
    courses = cart.courses.all() if cart else []

    total_units = sum(int(course.units) for course in courses)

    # Get the list of schedules for the current user
    schedules = Schedule.objects.filter(student=request.user)

    strms = ShoppingCart.objects.filter(user=request.user).values_list('strm', flat=True).distinct()
    strm_mapping = {
        1232: "Spring 2023",
        1238: "Fall 2023",
        1222: "Spring 2022",
        1228: "Fall 2022",
        1212: "Spring 2021",
        1218: "Fall 2021",
        1202: "Spring 2020",
        1208: "Fall 2020",
    }

    strm_names = [(strm, strm_mapping.get(strm, "")) for strm in strms]

    return render(request, 'student/cart.html', {
        'courses': courses,
        'strm_names': strm_names,
        'total_units': total_units,
        'schedules': schedules,  # Include the schedules queryset in the context
    })



@login_required
@student_required   
def add_to_cart(request, class_nbr, strm): 
    course = Course.objects.get(class_nbr=class_nbr)
    cart, created = ShoppingCart.objects.get_or_create(user= request.user, strm=strm)
    cart.courses.add(course)
    return redirect('shopping_cart')

@login_required
@student_required
def remove_from_cart(request, class_nbr):
    course = Course.objects.get(class_nbr=class_nbr)
    strm = request.GET.get('strm')
    if strm:
        cart = ShoppingCart.objects.filter(user = request.user, strm=int(strm)).first()
    else:
        cart = ShoppingCart.objects.first()
    
    if cart:
        cart.courses.remove(course)
    return redirect('shopping_cart')

def search_results(request):
    base_url = 'https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch'
    term = request.GET.get('term')
    subject = request.GET.get('subject')
    url = f'{base_url}?institution=UVA01&term={term}&subject={subject}&page=1'
    return redirect(url)

@login_required
def flexible_index(request):
    """ simple view that sends students and advisors to the appropriate index/home page """
    if request.user.is_advisor:
        return HttpResponseRedirect(reverse('advisor'))
    else:
        return HttpResponseRedirect(reverse('student'))

@login_required
def schedule_list(request):
    """ simple view that sends students and advisors to the appropriate schedule list page """
    if request.user.is_advisor:
        return HttpResponseRedirect(reverse('advisor-schedule-list'))
    else:
        return HttpResponseRedirect(reverse('student-schedule-list'))

@login_required
def schedule_detail(request, pk):
    """ simple view that sends students and advisors to the appropriate schedule detail page """
    if request.user.is_advisor:
        return HttpResponseRedirect(reverse('advisor-schedule-detail', args=(pk,)))
    else:
        return HttpResponseRedirect(reverse('student-schedule-detail', args=(pk,)))

@login_required
@student_required
def student_schedule_add_course(request):
    """ add a course to a schedule """
    schedule_id = request.POST['sched-id']
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    class_nbr = request.POST['class_nbr']
    course = Course.objects.get(pk = class_nbr)


    # if the course isn't in the schedule already
    add_class = not schedule.courses.filter(pk=class_nbr).exists()
    conflicting_courses = []

    # check to see if the course conflicts with any course currently in the schedule
    for current_course in schedule.courses.all():
        if course.conflicts_with(current_course):
            conflicting_courses.append(current_course)
            add_class = False

    if add_class:
        schedule.courses.add(course)
    else:
        messages.error(request, f"{course} could not be added to this schedule because it conflicts with these courses: {*conflicting_courses,} ")

    return HttpResponseRedirect(reverse("student-schedule-detail", args=(schedule_id,)))

@login_required
@student_required
def student_schedule_remove_course(request):
    """ remove a course from a schedule"""
    schedule_id = request.POST['sched-id']
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    class_nbr = request.POST['class_nbr']
    course = Course.objects.get(pk = class_nbr)

    schedule.courses.remove(course)
    return HttpResponseRedirect(reverse("student-schedule-detail", args=(schedule_id,)))

@login_required
def schedule_change_approval_status(request):
    """ Change the approval status of a schedule """
    schedule_id = request.POST['sched-id']
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    new_status = request.POST['new-status']
    
    if request.user.is_advisor:
        if new_status == ApprovalStatus.AP.value or new_status == ApprovalStatus.DN.value or new_status == ApprovalStatus.PD.value:
            schedule.approval_status = ApprovalStatus(new_status).value
            schedule.save()
        else:
            messages.error(request, "Not a valid status for an advisor")
    else:
        if new_status == ApprovalStatus.PD.value or new_status == ApprovalStatus.UN.value:
            schedule.approval_status = ApprovalStatus(new_status).value
            schedule.save()
        else:
            messages.error(request, "Not a valid status for a student")
    return HttpResponseRedirect(reverse("schedule-detail", args=(schedule_id,)))

# ------- Class-Based views for use with models and other more complex things -------

# ------- ------- Advisor Views ------- -------
@method_decorator([login_required, advisor_required], name='dispatch')
class AdvisorIndexView(generic.ListView):
    """
    default landing page for an advisor
    """
    template_name = 'advisor/index.html'
    model = User

@method_decorator([login_required, advisor_required], name='dispatch')
class AdvisorScheduleListView(generic.ListView):
    """
    list of an advisor's schedules
    """
    model = Schedule
    template_name = 'advisor/schedule_list.html'
    context_object_name = 'schedules'

    def get_queryset(self):
        """
        grab all of the advisor's schedules
        """
        return Schedule.objects.all()

@method_decorator([login_required, advisor_required], name='dispatch')
class AdvisorScheduleDetailView(generic.DetailView):
    """
    detail view for one of an advisor's schedules
    """
    model = Schedule
    template_name = 'advisor/schedule_detail.html'
    context_object_name = 'schedule'

# ------- ------- Student Views ------- -------

@method_decorator([login_required, student_required], name='dispatch')
class StudentIndexView(generic.ListView):
    """
    default landing page for a student
    """
    template_name = 'student/index.html'
    model = User

@method_decorator([login_required, student_required], name='dispatch')
class StudentScheduleListView(generic.ListView):
    """
    list of a student's schedules
    """
    model = Schedule
    template_name = 'student/schedule_list.html'
    context_object_name = 'schedules'

    def get_queryset(self):
        """
        grab all of the student's schedules
        """
        return Schedule.objects.filter(student=self.request.user)

@method_decorator([login_required, student_required], name='dispatch')
class StudentScheduleDetailView(generic.DetailView):
    """
    detial view of one of a student's schedules
    """
    model = Schedule
    template_name = 'student/schedule_detail.html'
    context_object_name = 'schedule'

@method_decorator([login_required, student_required], name='dispatch')
class ScheduleCreateView(CreateView):
    """ Create a new schedule """
    template_name = 'student/schedule_form.html'
    model = Schedule
    fields = ['approver', 'name']

    def get_form(self, *args, **kwargs):
        """ limit the choices for approver to users that are advisors. """
        form = super(ScheduleCreateView, self).get_form(*args, **kwargs)
        form.fields['approver'].queryset = User.objects.filter(is_advisor=True)
        return form

    def form_valid(self, form, *args, **kwargs):
        """ this can be used for validation, but we also use it to add things to the form """
        form.instance.student = self.request.user
        return super(ScheduleCreateView, self).form_valid(form, *args, **kwargs)

@method_decorator([login_required, student_required], name='dispatch')
class ScheduleDeleteView(DeleteView):
    """ Delete a schedule """
    model = Schedule
    template_name = 'student/schedule_confirm_delete.html'
    success_url = reverse_lazy('student-schedule-list')
