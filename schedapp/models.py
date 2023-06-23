# pylint: disable=no-member

from enum import Enum
from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse

# ------- User Model -------
class User(AbstractUser):
    """
    abstract user that adds multiple user type support
    """
    # advisors must be manually declared as such by an admin (for now)
    is_advisor = models.BooleanField(default=False)
    name = models.CharField(max_length=70, blank=True, null=True)
    # the list of people who are either your advisees if you are an advisor
    # or your advisors if you are a student
    symbiotes = models.ManyToManyField("User",
                                       blank=True,
                                       related_name="symbiotes_of")
    def __str__(self):
        return f'{self.name} {"(an advisor)" if self.is_advisor else ""}'

    def save(self, *args, **kwargs):
        if self.first_name != "" or self.last_name != "":
            self.name = f"{self.first_name} {self.last_name}"
        else:
            self.name = self.username
        super(User, self).save(*args, **kwargs)

# ------- Other Models -------
class Other_Course(models.Model):
    """
    Represents a course's information from the SIS api    
    """
    subject                 = models.CharField(max_length=10)
    catalog_number          = models.CharField(max_length=20)
    class_section           = models.CharField(max_length=20)
    class_number            = models.IntegerField(primary_key=True)
    class_title             = models.CharField(max_length=250)
    class_topic_formal_desc = models.CharField(max_length=600)
    instructor              = models.CharField(max_length=200)
    enrollment_capacity     = models.IntegerField()
    meeting_days            = models.CharField(max_length=10)
    meeting_time_start      = models.CharField(max_length=10)
    meeting_time_end        = models.CharField(max_length=10)
    term                    = models.CharField(max_length=10)
    term_desc               = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.subject} {self.catalog_number} {self.class_title} ({self.meeting_time_start} to {self.meeting_time_end}) {self.term_desc}'
        
class Course(models.Model):
    index                  = models.CharField(max_length=255, blank=True, null=True)
    crse_id                = models.CharField(max_length=255, blank=True, null=True)
    crse_offer_nbr         = models.IntegerField(blank=True, null=True)
    strm                   = models.CharField(max_length=255, blank=True, null=True)
    session_code           = models.CharField(max_length=255, blank=True, null=True)
    session_descr          = models.CharField(max_length=255, blank=True, null=True)
    class_section          = models.CharField(max_length=255, blank=True, null=True)
    location               = models.CharField(max_length=255, blank=True, null=True)
    location_descr         = models.CharField(max_length=255, blank=True, null=True)
    start_dt               = models.CharField(max_length=255, blank=True, null=True)
    end_dt                 = models.CharField(max_length=255, blank=True, null=True)
    class_stat             = models.CharField(max_length=255, blank=True, null=True)
    campus                 = models.CharField(max_length=255, blank=True, null=True)
    campus_descr           = models.CharField(max_length=255, blank=True, null=True)
    class_nbr              = models.IntegerField(primary_key=True)
    acad_career            = models.CharField(max_length=255, blank=True, null=True)
    acad_career_descr      = models.CharField(max_length=255, blank=True, null=True)
    component              = models.CharField(max_length=255, blank=True, null=True)
    subject                = models.CharField(max_length=255, blank=True, null=True)
    subject_descr          = models.CharField(max_length=255, blank=True, null=True)
    catalog_nbr            = models.CharField(max_length=255, blank=True, null=True)
    class_type             = models.CharField(max_length=255, blank=True, null=True)
    schedule_print         = models.CharField(max_length=255, blank=True, null=True)
    acad_group             = models.CharField(max_length=255, blank=True, null=True)
    instruction_mode       = models.CharField(max_length=255, blank=True, null=True)
    instruction_mode_descr = models.CharField(max_length=255, blank=True, null=True)
    acad_org               = models.CharField(max_length=255, blank=True, null=True)
    wait_tot               = models.IntegerField(blank=True, null=True)
    wait_cap               = models.IntegerField(blank=True, null=True)
    class_capacity         = models.IntegerField(blank=True, null=True)
    enrollment_total       = models.IntegerField(blank=True, null=True)
    enrollment_available   = models.IntegerField(blank=True, null=True)
    descr                  = models.TextField()
    rqmnt_designtn         = models.CharField(max_length=255, blank=True, null=True)
    units                  = models.CharField(max_length=255, blank=True, null=True)
    combined_section       = models.CharField(max_length=255, blank=True, null=True)
    enrl_stat              = models.CharField(max_length=255, blank=True, null=True)
    enrl_stat_descr        = models.CharField(max_length=255, blank=True, null=True)
    topic                  = models.CharField(max_length=255, blank=True, null=True)
    instructors            = models.JSONField(encoder=DjangoJSONEncoder)
    section_type           = models.CharField(max_length=255, blank=True, null=True)
    meetings               = models.JSONField(encoder=DjangoJSONEncoder)
    crse_attr              = models.CharField(max_length=255, blank=True, null=True)
    crse_attr_value        = models.CharField(max_length=255, blank=True, null=True)
    reserve_caps           = models.JSONField(encoder=DjangoJSONEncoder)

    def __str__(self):
            return f'{self.subject} {self.catalog_nbr}'

    def conflicts_with(self, course):     
        """ check if the time of this course conflicts with another """
        self_meetings = self.meetings
        course_meetings = course.meetings
        
        # check if term overlaps
        if self.strm == course.strm:
            # check if days overlap
            self_days = self_meetings[0]['days']
            course_days = course_meetings[0]['days']

            # we are going to assume that there are only two-letter date codes in our database . . .
            course_days_list = [course_days[i:i+2] for i in range(0, len(course_days), 2)]

            for day in [self_days[i:i+2] for i in range(0, len(self_days), 2)]:
                if day in course_days_list:
                    # check if times overlap
                    # either the start of the other course needs to be after the end of this course
                    # or the end of the other course needs to be before the start of this course

                    other_course_after = datetime.strptime(course_meetings[0]['start_time'], '%I:%M %p') > datetime.strptime(self_meetings[0]['end_time'], '%I:%M %p')
                    other_course_before = datetime.strptime(self_meetings[0]['start_time'], '%I:%M %p') > datetime.strptime(course_meetings[0]['end_time'], '%I:%M %p')
                    
                    if not other_course_after and not other_course_before:
                        # they must overlap
                        return True

        # if we get to here, then we didn't have any overlapping times
        return False

def addJsonCourse(course):
    """
    adds a course in json representation to the database if it doesn't exist therein already
    returns the course regardless.
    """
    class_nbr_local = course['class_nbr']
    try: 
        result = Course.objects.get(pk = class_nbr_local)
    except Course.DoesNotExist:   
        index = course['index']
        crse_id  = course['crse_id']
        crse_offer_nbr = course['crse_offer_nbr']
        strm = course['strm']
        session_code = course['session_code']
        session_descr = course['session_descr']
        class_section = course['class_section']
        location = course['location']
        location_descr = course['location_descr']
        start_dt = course['start_dt']
        end_dt = course['end_dt']
        class_stat = course['class_stat']
        campus = course['campus']
        campus_descr = course['campus_descr']
        acad_career = course['acad_career']
        acad_career_descr  = course['acad_career_descr']
        component              = course['component']
        subject                = course['subject']
        subject_descr          = course['subject_descr']
        catalog_nbr            = course['catalog_nbr']
        class_type             = course['class_type']
        schedule_print         = course['schedule_print']
        acad_group             = course['acad_group']
        instruction_mode       = course['instruction_mode']
        instruction_mode_descr = course['instruction_mode_descr']
        acad_org               = course['acad_org']
        wait_tot               = course['wait_tot']
        wait_cap               = course['wait_cap']
        class_capacity         = course['class_capacity']
        enrollment_total       = course['enrollment_total']
        enrollment_available   = course['enrollment_available']
        descr                  = course['descr']
        rqmnt_designtn         = course['rqmnt_designtn']
        units                  = course['units']
        combined_section       = course['combined_section']
        enrl_stat              = course['enrl_stat']
        enrl_stat_descr        = course['enrl_stat_descr']
        topic                  = course['topic']
        instructors            = course['instructors']
        section_type           = course['section_type']
        meetings               = course['meetings']
        crse_attr              = course['crse_attr']
        crse_attr_value        = course['crse_attr_value']
        reserve_caps           = course['reserve_caps']

        result = Course.objects.create(
            index = index,
            crse_id = crse_id,
            crse_offer_nbr = crse_offer_nbr,
            strm = strm,
            session_code = session_code,
            session_descr = session_descr,
            class_section = class_section,
            location = location,
            location_descr = location_descr,
            start_dt = start_dt,
            end_dt = end_dt,
            class_stat = class_stat,
            campus = campus,
            campus_descr = campus_descr,
            class_nbr = class_nbr_local,
            acad_career = acad_career,
            acad_career_descr = acad_career_descr,
            component = component,
            subject = subject,
            subject_descr = subject_descr,
            catalog_nbr = catalog_nbr,
            class_type = class_type,
            schedule_print = schedule_print,
            acad_group = acad_group,
            instruction_mode = instruction_mode,
            instruction_mode_descr = instruction_mode_descr,
            acad_org = acad_org,
            wait_tot = wait_tot,
            wait_cap = wait_cap,
            class_capacity = class_capacity,
            enrollment_total = enrollment_total,
            enrollment_available = enrollment_available,
            descr = descr,
            rqmnt_designtn = rqmnt_designtn,
            units = units,
            combined_section = combined_section,
            enrl_stat = enrl_stat,
            enrl_stat_descr = enrl_stat_descr,
            topic = topic,
            instructors = instructors,
            section_type = section_type,
            meetings = meetings,
            crse_attr = crse_attr,
            crse_attr_value = crse_attr_value,
            reserve_caps = reserve_caps)
        result.save()
    return result

class ApprovalStatus(Enum):
    """ an enum for the possible approval status. We can add more if necessary"""
    UN = "unsubmitted"
    PD = "pending"
    AP = "approved"
    DN = "denied"

class Schedule(models.Model):
    """
    represents a class schedule
    """
    student = models.ForeignKey(get_user_model(),
                                on_delete=models.CASCADE,
                                related_name="myschedules")
    approver = models.ForeignKey(get_user_model(),
                                 on_delete=models.CASCADE,
                                 related_name="schedules")
    name = models.CharField(max_length=200)
    other_courses = models.ManyToManyField(Other_Course, blank=True)
    courses = models.ManyToManyField(Course, blank=True)
    approval_status = models.CharField(max_length=60, choices=[(status.value, status.name) for status in ApprovalStatus], default=ApprovalStatus.UN.value, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('student-schedule-list')
    
    def __str__(self):
        return f'{self.name}'
    
class ShoppingCart(models.Model): 
    user = models.ForeignKey(get_user_model(),
                                on_delete=models.CASCADE, default=None)
    strm = models.IntegerField(default=1228)
    courses = models.ManyToManyField(Course)

    def __str__(self):
        return f'{self.strm} Cart'

