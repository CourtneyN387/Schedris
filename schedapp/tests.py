# pylint: disable=no-member
# pylint: disable=missing-function-docstring
import json
from django.test import TestCase, Client
from datetime import datetime
from django.urls import reverse
from unittest.mock import patch, Mock
from django.http import HttpRequest
from .views import *
from .models import Other_Course, User, Schedule, addJsonCourse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


User = get_user_model()
# ------- Functions for creating instances of models -------
class Builders(TestCase):
    """
    Functions for creating instances of models
    """
    def create_other_course(
            self,
            subject                 : str = "XMPL",
            catalog_number          : str = "0000",
            class_section           : str = "0000",
            class_number            : int = 00000,
            class_title             : str = "Example of a Course",
            class_topic_formal_desc : str = "Example of a Course is a course in exactly what it sounds like",
            instructor              : str = "Cadwallader, Guy",
            enrollment_capacity     : int = 7,
            meeting_days            : str = "MWF",
            meeting_time_start      : str = "11:00:00",
            meeting_time_end        : str = "12:15:00",
            term                    : str = "1238",
            term_desc               : str = "2023 Fall"
    ):
        """
        Creates a course object with reasonable defaults.
        """
        return Other_Course.objects.create(
            subject                 = subject,
            catalog_number          = catalog_number,
            class_section           = class_section,
            class_number            = class_number,
            class_title             = class_title,
            class_topic_formal_desc = class_topic_formal_desc,
            instructor              = instructor,
            enrollment_capacity     = enrollment_capacity,
            meeting_days            = meeting_days,
            meeting_time_start      = meeting_time_start,
            meeting_time_end        = meeting_time_end,
            term                    = term,
            term_desc               = term_desc
        )

    def create_course(self, json_course = None):
        if not json_course:
            course_string = '{"index": 92, "crse_id": "043734", "crse_offer_nbr": 1, "strm": "1232", "session_code": "SRT", "session_descr": "Short Add", "class_section": "001", "location": "MAIN", "location_descr": "On Grounds", "start_dt": "01/18/2023", "end_dt": "05/02/2023", "class_stat": "A", "campus": "MAIN", "campus_descr": "Main Campus", "class_nbr": 20052, "acad_career": "GRAD", "acad_career_descr": "Graduate", "component": "LEC", "subject": "SYS", "subject_descr": "Systems & Information Engr", "catalog_nbr": "6042", "class_type": "E", "schedule_print": "Y", "acad_group": "ENGR", "instruction_mode": "P", "instruction_mode_descr": "In Person", "acad_org": "ESE", "wait_tot": 0, "wait_cap": 0, "class_capacity": 36, "enrollment_total": 9, "enrollment_available": 27, "descr": "Network and Combinatorial Optimization", "rqmnt_designtn": "", "units": "3", "combined_section": "N", "enrl_stat": "O", "enrl_stat_descr": "Open", "topic": "", "instructors": [{"name": "Thomas Lidbetter", "email": "ctk5xz@virginia.edu"}], "section_type": "Lecture", "meetings": [{"days": "TuTh", "start_time": "12:30 PM", "end_time": "01:45 PM", "start_dt": "01/18/2023", "end_dt": "05/02/2023", "bldg_cd": "THN", "bldg_has_coordinates": true, "facility_descr": "Thornton Hall D222", "room": "D222", "facility_id": "THN D222", "instructor": "Thomas Lidbetter"}], "crse_attr": "", "crse_attr_value": "", "reserve_caps": []}'
            course = json.loads(course_string)
            return addJsonCourse(course)
        return addJsonCourse(json_course)

    def create_user(
            self,
            is_advisor = False,
            name       = "Bob Alice",
            symbiotes  = None
    ):
        """
        Creates a user object with reasonable defaults, but
        no symbiotes (advisors or students) unless you pass
        them in
        """
        username = f"{name}{datetime.now()}" # so the username is unique
        user =  User.objects.create(is_advisor = is_advisor, name = name, username = username)
        user.save()
        if symbiotes:
            user.symbiotes.add(symbiotes)

        return user

    def create_student(self, name="student"):
        """
        creates a student named "student", with advisors "advisor1"
        and "advisor2"
        """
        advisor1 = self.create_user(is_advisor=True,  name="advisor1")
        advisor2 = self.create_user(is_advisor=True,  name="advisor2")
        student  = self.create_user(is_advisor=False, name=name)
        student.symbiotes.add(advisor1)
        student.symbiotes.add(advisor2)
        return student

    def create_advisor(self, name="advisor"):
        """
        creates an advisor named "advisor", with students "student1"
        and "student2"
        """
        student1 = self.create_user(is_advisor=False, name="student1")
        student2 = self.create_user(is_advisor=False, name="student2")
        advisor  = self.create_user(is_advisor=True,  name=name)
        advisor.symbiotes.add(student1)
        advisor.symbiotes.add(student2)
        return advisor

    def create_schedule(
            self,
            student  = None,
            approver = None,
            name     = "example-schedule",
            courses  = None
    ):
        """
        Creates a schedule object with reasonable defaults
        including 1 example course
        """
        schedule = Schedule.objects.create(
            student  = self.create_student(name="Jane Student") if not student else student,
            approver = self.create_advisor(name="John Advisor") if not approver else approver,
            name     = name,
        )
        if not courses:
            schedule.courses.add(self.create_course())
        else:
            for course in courses:
                schedule.courses.add(course)
            
        return schedule

# ------- Model-Based Tests ------- 
class CourseModelTests(TestCase):
    """
    Tests for the Course model
    """
    def conflicts_with_on_self_is_true(self):
        this_course = Builders().create_course()
        self.assertTrue(this_course.conflicts_with(this_course))

    def conflicts_with_for_course_that_has_different_days_is_false(self):
        course_json = '{"index": 92, "crse_id": "043734", "crse_offer_nbr": 1, "strm": "1232", "session_code": "SRT", "session_descr": "Short Add", "class_section": "001", "location": "MAIN", "location_descr": "On Grounds", "start_dt": "01/18/2023", "end_dt": "05/02/2023", "class_stat": "A", "campus": "MAIN", "campus_descr": "Main Campus", "class_nbr": 20052, "acad_career": "GRAD", "acad_career_descr": "Graduate", "component": "LEC", "subject": "SYS", "subject_descr": "Systems & Information Engr", "catalog_nbr": "6042", "class_type": "E", "schedule_print": "Y", "acad_group": "ENGR", "instruction_mode": "P", "instruction_mode_descr": "In Person", "acad_org": "ESE", "wait_tot": 0, "wait_cap": 0, "class_capacity": 36, "enrollment_total": 9, "enrollment_available": 27, "descr": "Network and Combinatorial Optimization", "rqmnt_designtn": "", "units": "3", "combined_section": "N", "enrl_stat": "O", "enrl_stat_descr": "Open", "topic": "", "instructors": [{"name": "Thomas Lidbetter", "email": "ctk5xz@virginia.edu"}], "section_type": "Lecture", "meetings": [{"days": "MoWe", "start_time": "12:30 PM", "end_time": "01:45 PM", "start_dt": "01/18/2023", "end_dt": "05/02/2023", "bldg_cd": "THN", "bldg_has_coordinates": true, "facility_descr": "Thornton Hall D222", "room": "D222", "facility_id": "THN D222", "instructor": "Thomas Lidbetter"}], "crse_attr": "", "crse_attr_value": "", "reserve_caps": []}'
        this_course = Builders().create_course()
        different_course = Builders.create_couse(course_json)
        self.assertFalse(this_course.conflicts_with(different_course))

    def conflicts_with_for_course_that_has_one_same_day_is_true(self):
        course_json = '{"index": 92, "crse_id": "043734", "crse_offer_nbr": 1, "strm": "1232", "session_code": "SRT", "session_descr": "Short Add", "class_section": "001", "location": "MAIN", "location_descr": "On Grounds", "start_dt": "01/18/2023", "end_dt": "05/02/2023", "class_stat": "A", "campus": "MAIN", "campus_descr": "Main Campus", "class_nbr": 20052, "acad_career": "GRAD", "acad_career_descr": "Graduate", "component": "LEC", "subject": "SYS", "subject_descr": "Systems & Information Engr", "catalog_nbr": "6042", "class_type": "E", "schedule_print": "Y", "acad_group": "ENGR", "instruction_mode": "P", "instruction_mode_descr": "In Person", "acad_org": "ESE", "wait_tot": 0, "wait_cap": 0, "class_capacity": 36, "enrollment_total": 9, "enrollment_available": 27, "descr": "Network and Combinatorial Optimization", "rqmnt_designtn": "", "units": "3", "combined_section": "N", "enrl_stat": "O", "enrl_stat_descr": "Open", "topic": "", "instructors": [{"name": "Thomas Lidbetter", "email": "ctk5xz@virginia.edu"}], "section_type": "Lecture", "meetings": [{"days": "TuWe", "start_time": "12:30 PM", "end_time": "01:45 PM", "start_dt": "01/18/2023", "end_dt": "05/02/2023", "bldg_cd": "THN", "bldg_has_coordinates": true, "facility_descr": "Thornton Hall D222", "room": "D222", "facility_id": "THN D222", "instructor": "Thomas Lidbetter"}], "crse_attr": "", "crse_attr_value": "", "reserve_caps": []}'
        this_course = Builders().create_course()
        different_course = Builders.create_couse(course_json)
        self.assertTrue(this_course.conflicts_with(different_course))

    def conflicts_with_for_course_that_has_different_strm_is_false(self):
        course_json = '{"index": 92, "crse_id": "043734", "crse_offer_nbr": 1, "strm": "1238", "session_code": "SRT", "session_descr": "Short Add", "class_section": "001", "location": "MAIN", "location_descr": "On Grounds", "start_dt": "01/18/2023", "end_dt": "05/02/2023", "class_stat": "A", "campus": "MAIN", "campus_descr": "Main Campus", "class_nbr": 20052, "acad_career": "GRAD", "acad_career_descr": "Graduate", "component": "LEC", "subject": "SYS", "subject_descr": "Systems & Information Engr", "catalog_nbr": "6042", "class_type": "E", "schedule_print": "Y", "acad_group": "ENGR", "instruction_mode": "P", "instruction_mode_descr": "In Person", "acad_org": "ESE", "wait_tot": 0, "wait_cap": 0, "class_capacity": 36, "enrollment_total": 9, "enrollment_available": 27, "descr": "Network and Combinatorial Optimization", "rqmnt_designtn": "", "units": "3", "combined_section": "N", "enrl_stat": "O", "enrl_stat_descr": "Open", "topic": "", "instructors": [{"name": "Thomas Lidbetter", "email": "ctk5xz@virginia.edu"}], "section_type": "Lecture", "meetings": [{"days": "TuTh", "start_time": "12:30 PM", "end_time": "01:45 PM", "start_dt": "01/18/2023", "end_dt": "05/02/2023", "bldg_cd": "THN", "bldg_has_coordinates": true, "facility_descr": "Thornton Hall D222", "room": "D222", "facility_id": "THN D222", "instructor": "Thomas Lidbetter"}], "crse_attr": "", "crse_attr_value": "", "reserve_caps": []}'
        this_course = Builders().create_course()
        different_course = Builders.create_couse(course_json)
        self.assertFalse(this_course.conflicts_with(different_course))

    def conflicts_with_for_course_that_has_overlapping_time_is_true(self):
        course_json = '{"index": 92, "crse_id": "043734", "crse_offer_nbr": 1, "strm": "1232", "session_code": "SRT", "session_descr": "Short Add", "class_section": "001", "location": "MAIN", "location_descr": "On Grounds", "start_dt": "01/18/2023", "end_dt": "05/02/2023", "class_stat": "A", "campus": "MAIN", "campus_descr": "Main Campus", "class_nbr": 20052, "acad_career": "GRAD", "acad_career_descr": "Graduate", "component": "LEC", "subject": "SYS", "subject_descr": "Systems & Information Engr", "catalog_nbr": "6042", "class_type": "E", "schedule_print": "Y", "acad_group": "ENGR", "instruction_mode": "P", "instruction_mode_descr": "In Person", "acad_org": "ESE", "wait_tot": 0, "wait_cap": 0, "class_capacity": 36, "enrollment_total": 9, "enrollment_available": 27, "descr": "Network and Combinatorial Optimization", "rqmnt_designtn": "", "units": "3", "combined_section": "N", "enrl_stat": "O", "enrl_stat_descr": "Open", "topic": "", "instructors": [{"name": "Thomas Lidbetter", "email": "ctk5xz@virginia.edu"}], "section_type": "Lecture", "meetings": [{"days": "TuTh", "start_time": "11:30 PM", "end_time": "01:45 PM", "start_dt": "01/18/2023", "end_dt": "05/02/2023", "bldg_cd": "THN", "bldg_has_coordinates": true, "facility_descr": "Thornton Hall D222", "room": "D222", "facility_id": "THN D222", "instructor": "Thomas Lidbetter"}], "crse_attr": "", "crse_attr_value": "", "reserve_caps": []}'
        this_course = Builders().create_course()
        different_course = Builders.create_couse(course_json)
        self.assertTrue(this_course.conflicts_with(different_course))

class ScheduleModelTests(TestCase):
    """
    Tests for the Schedule model
    """
    def test_something(self):
        print(self.__str__())
        self.assertEqual(1, 1)

class UserModelTests(TestCase):
    """
    Tests for the User model
    """
    def test_something(self):
        print(self.__str__())
        self.assertEqual(1, 1)
    

# ------- View-Based Tests ------- 
class CourseListViewTests(TestCase):
    """
    Tests for the course_list view
    """
    #test to see if view works
    def test_url(self):
        response = self.client.get(reverse('course_list')) 
        self.assertEqual(response.status_code, 302)
    #test with mock data from SIS API
    def test_APMA(self):
        mock_data = [{"index":1,"crse_id":"001140","crse_offer_nbr":1,"strm":"1228","session_code":"SRT","session_descr":"Short Add","class_section":"002","location":"MAIN","location_descr":"On Grounds","start_dt":"08/23/2022","end_dt":"12/06/2022","class_stat":"A","campus":"MAIN","campus_descr":"Main Campus","class_nbr":15529,"acad_career":"UGRD","acad_career_descr":"Undergraduate","component":"LEC","subject":"APMA","subject_descr":"Applied Mathematics","catalog_nbr":"1110","class_type":"E","schedule_print":"Y","acad_group":"ENGR","instruction_mode":"P","instruction_mode_descr":"In Person","acad_org":"APMA","wait_tot":0,"wait_cap":0,"class_capacity":45,"enrollment_total":44,"enrollment_available":1,"descr":"Single Variable Calculus II","rqmnt_designtn":"","units":"4","combined_section":"N","enrl_stat":"O","enrl_stat_descr":"Open","topic":"","instructors":[{"name":"Monika Abramenko","email":"ma2ke@virginia.edu"}],"section_type":"Lecture","meetings":[{"days":"Tu","start_time":"13.00.00.000000-05:00","end_time":"13.50.00.000000-05:00","start_dt":"08/23/2022","end_dt":"12/06/2022","bldg_cd":"OLS","bldg_has_coordinates":'true',"facility_descr":"Olsson Hall 005","room":"005","facility_id":"OLS 005","instructor":"Monika Abramenko"},{"days":"MoWeFr","start_time":"09.00.00.000000-05:00","end_time":"09.50.00.000000-05:00","start_dt":"08/23/2022","end_dt":"12/06/2022","bldg_cd":"OLS","bldg_has_coordinates":'true',"facility_descr":"Olsson Hall 005","room":"005","facility_id":"OLS 005","instructor":"Monika Abramenko"}],"crse_attr":"","crse_attr_value":"","reserve_caps":[]},{"index":2,"crse_id":"001151","crse_offer_nbr":1,"strm":"1228","session_code":"SRT","session_descr":"Short Add","class_section":"001","location":"MAIN","location_descr":"On Grounds","start_dt":"08/23/2022","end_dt":"12/06/2022","class_stat":"A","campus":"MAIN","campus_descr":"Main Campus","class_nbr":15537,"acad_career":"UGRD","acad_career_descr":"Undergraduate","component":"LEC","subject":"APMA","subject_descr":"Applied Mathematics","catalog_nbr":"3080","class_type":"E","schedule_print":"Y","acad_group":"ENGR","instruction_mode":"P","instruction_mode_descr":"In Person","acad_org":"APMA","wait_tot":0,"wait_cap":0,"class_capacity":45,"enrollment_total":43,"enrollment_available":2,"descr":"Linear Algebra","rqmnt_designtn":"","units":"3","combined_section":"N","enrl_stat":"O","enrl_stat_descr":"Open","topic":"","instructors":[{"name":"Monika Abramenko","email":"ma2ke@virginia.edu"}],"section_type":"Lecture","meetings":[{"days":"MoWeFr","start_time":"12.00.00.000000-05:00","end_time":"12.50.00.000000-05:00","start_dt":"08/23/2022","end_dt":"12/06/2022","bldg_cd":"CHE","bldg_has_coordinates":'true',"facility_descr":"Chemical Engineering Bldg 005","room":"005","facility_id":"CHE 005","instructor":"Monika Abramenko"}],"crse_attr":"","crse_attr_value":"","reserve_caps":[]},{"index":3,"crse_id":"001151","crse_offer_nbr":1,"strm":"1228","session_code":"SRT","session_descr":"Short Add","class_section":"003","location":"MAIN","location_descr":"On Grounds","start_dt":"08/23/2022","end_dt":"12/06/2022","class_stat":"A","campus":"MAIN","campus_descr":"Main Campus","class_nbr":15539,"acad_career":"UGRD","acad_career_descr":"Undergraduate","component":"LEC","subject":"APMA","subject_descr":"Applied Mathematics","catalog_nbr":"3080","class_type":"E","schedule_print":"Y","acad_group":"ENGR","instruction_mode":"P","instruction_mode_descr":"In Person","acad_org":"APMA","wait_tot":0,"wait_cap":0,"class_capacity":45,"enrollment_total":38,"enrollment_available":7,"descr":"Linear Algebra","rqmnt_designtn":"","units":"3","combined_section":"N","enrl_stat":"O","enrl_stat_descr":"Open","topic":"","instructors":[{"name":"Monika Abramenko","email":"ma2ke@virginia.edu"}],"section_type":"Lecture","meetings":[{"days":"MoWeFr","start_time":"11.00.00.000000-05:00","end_time":"11.50.00.000000-05:00","start_dt":"08/23/2022","end_dt":"12/06/2022","bldg_cd":"CHE","bldg_has_coordinates":'true',"facility_descr":"Chemical Engineering Bldg 005","room":"005","facility_id":"CHE 005","instructor":"Monika Abramenko"}],"crse_attr":"","crse_attr_value":"","reserve_caps":[]}]
        mock_response = Mock(status_code=200, json=lambda: mock_data)
        with patch('requests.get') as get_mock:
            response = self.client.get(reverse('course_list')) 
            response.json.return_value = mock_data
            response.status_code = 200
            get_mock.return_value = response
        get_mock.return_value = mock_response.json()
        print(get_mock)
        self.assertIn("001140", [course_info["crse_id"] for course_info in get_mock.return_value])
        self.assertNotIn("AM", [course_info["subject"] for course_info in get_mock.return_value])

    #1222, APMA
    def test_Term_Subject(self):
        self.user = Builders().create_user()
        self.user.set_password("teswert24325@$d")
        self.user.save()
        self.client.force_login(self.user)
        response = self.client.get("http://127.0.0.1:8000/courses/?keyword=&Term=1222&department=APMA&subject=&location=&instruct_modes=&session_code=&catalog=")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "APMA 1000 - Preparation for Engineering Mathematics")
        self.assertContains(response, "Section: 001")
        self.assertContains(response, "Status: 1/15")
        self.assertContains(response, "Days: Th")
        self.assertContains(response, "Room: Mechanical Engineering 305")
    #1228, abramenko
    def test_Term_Keyword(self):
        self.user = Builders().create_user()
        self.user.set_password("teswert24325@$d")
        self.user.save()
        self.client.force_login(self.user)
        response = self.client.get("http://127.0.0.1:8000/courses/?keyword=abramenko&Term=1228&department=&subject=&location=&instruct_modes=&session_code=&catalog=")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "APMA 1110 - Single Variable Calculus II")
        self.assertContains(response, "APMA 3080 - Linear Algebra")
        self.assertContains(response, "MATH 3000 - Transition to Higher Mathematics")
        self.assertContains(response, "MATH 7600 - Homological Algebra")
        self.assertContains(response, "MATH 8998 - Non-Topical Research, Preparation for Research")
        self.assertContains(response, "MATH 9998 - Non-Topical Research, Preparation for Doctoral Research")
        self.assertContains(response, "MATH 9999 - Non-Topical Research")
    #1218, AAS
    def test_Term_Department(self):
        self.user = Builders().create_user()
        self.user.set_password("teswert24325@$d")
        self.user.save()
        self.client.force_login(self.user)
        response = self.client.get("http://127.0.0.1:8000/courses/?keyword=&Term=1218&department=AAS&subject=&location=&instruct_modes=&session_code=&catalog=")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AAS 1010 - Introduction to African-American and African Studies I")
        self.assertContains(response, "AAS 2224 - Black Femininities and Masculinities in the US Media")
        self.assertContains(response, "AAS 2559 - New Course in African and African American Studies")
        self.assertContains(response, "AAS 3645 - Musical Fictions")
        self.assertContains(response, "AAS 3710 - African Worlds through Life Stories")
        self.assertContains(response, "AAS 3810 - Race, Culture and Inequality")
    #1228, AAS, APMA
    def test_Term_Department_Subject_Conflict(self):
        self.user = Builders().create_user()
        self.user.set_password("teswert24325@$d")
        self.user.save()
        self.client.force_login(self.user)
        response = self.client.get("http://127.0.0.1:8000/courses/?keyword=&Term=1228&department=AAS&subject=APMA&location=&instruct_modes=&session_code=&catalog=")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "AAS 1010 - Introduction to African-American and African Studies I")
        self.assertNotContains(response, "AAS 2224 - Black Femininities and Masculinities in the US Media")
        self.assertNotContains(response, "AAS 2559 - New Course in African and African American Studies")
        self.assertNotContains(response, "AAS 3645 - Musical Fictions")
        self.assertNotContains(response, "AAS 3710 - African Worlds through Life Stories")
        self.assertNotContains(response, "AAS 3810 - Race, Culture and Inequality")
        self.assertNotContains(response, "APMA 1110 - Single Variable Calculus II")
        self.assertNotContains(response, "APMA 3080 - Linear Algebra")
        self.assertNotContains(response, "MATH 3000 - Transition to Higher Mathematics")
        self.assertNotContains(response, "MATH 7600 - Homological Algebra")
        self.assertNotContains(response, "MATH 8998 - Non-Topical Research, Preparation for Research")
        self.assertNotContains(response, "MATH 9998 - Non-Topical Research, Preparation for Doctoral Research")
        self.assertNotContains(response, "MATH 9999 - Non-Topical Research")
    #1228, APMA, UVA, In Person
    def test_Term_Department_Location_InstructionMode(self):
        self.user = Builders().create_user()
        self.user.set_password("teswert24325@$d")
        self.user.save()
        self.client.force_login(self.user)
        response = self.client.get("http://127.0.0.1:8000/courses/?keyword=&Term=1228&department=APMA&subject=&location=MAIN&instruct_modes=P&session_code=&catalog=")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "APMA 1090 - Single Variable Calculus I")
        self.assertContains(response, "APMA 1110 - Single Variable Calculus II")
        self.assertContains(response, "APMA 2120 - Multivariable Calculus")
        self.assertContains(response, "APMA 2130 - Ordinary Differential Equations")
        self.assertContains(response, "APMA 3080 - Linear Algebra")
        self.assertContains(response, "APMA 3100 - Probability")
        self.assertContains(response, "Instruction: In Person")
        self.assertNotContains(response, "Instruction: Hybrid")
        self.assertNotContains(response, "Instruction: Online Synchronous")
        self.assertContains(response, "APMA 3110 - Applied Statistics and Probability")
        self.assertContains(response, "APMA 3120 - Statistics")
    #1222, 1110
    def test_Term_catalognum(self):
        self.user = Builders().create_user()
        self.user.set_password("teswert24325@$d")
        self.user.save()
        self.client.force_login(self.user)
        response = self.client.get("http://127.0.0.1:8000/courses/?keyword=&Term=1222&department=&subject=&location=&instruct_modes=&session_code=&catalog=1110")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "APMA 1090 - Single Variable Calculus I")
        self.assertContains(response, "APMA 1110 - Single Variable Calculus II")
        self.assertContains(response, "CS 1110 - Introduction to Programming")
        self.assertContains(response, "MATH 1110 - Probability/Finite Mathematics")
        self.assertNotContains(response, "APMA 3080 - Linear Algebra")
        self.assertNotContains(response, "APMA 3100 - Probability")
    #1228, APMA, Short add
    def test_Term_Department_AcademicSession(self):
        
        self.user = Builders().create_user()
        self.user.set_password("teswert24325@$d")
        self.user.save()
        self.client.force_login(self.user)
        response = self.client.get("http://127.0.0.1:8000/courses/?keyword=&Term=1228&department=APMA&subject=&location=&instruct_modes=&session_code=SRT&catalog=")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "APMA 1090 - Single Variable Calculus I")
        self.assertContains(response, "APMA 1110 - Single Variable Calculus II")
        self.assertContains(response, "APMA 2120 - Multivariable Calculus")
        self.assertContains(response, "APMA 2130 - Ordinary Differential Equations")
        self.assertContains(response, "APMA 3100 - Probability")

class ScheduleListViewTests(TestCase):
    """
    Tests the schedule_list view, as well as the student_schedule_list
    and advisor_schedule_list views
    """
    @classmethod
    def setUpTestData(cls):
        """ initialization to be run before all tests in this class """
        cls.student_bob = Builders().create_student(name="bob")
        cls.advisor_mack = Builders().create_advisor(name="mack")
        cls.advisor_mack.symbiotes.add(cls.student_bob)
        cls.course = Builders().create_course()
        cls.schedule = Builders().create_schedule(student=cls.student_bob, approver=cls.advisor_mack, name="bobs_schedule", courses=[cls.course])
    
    def setUp(self):
        """ refresh variables from the db before each test run """
        self.student_bob.refresh_from_db()
        self.advisor_mack.refresh_from_db()
        self.course.refresh_from_db()
        self.schedule.refresh_from_db()

    def test_schedule_list_url_student_redirect(self):
        req = HttpRequest()
        req.method = 'GET'
        req.user = self.student_bob
        req.follow = True
        response = schedule_list(req)
        self.assertTrue(reverse('student-schedule-list') in response.url)

    def test_schedule_list_url_advisor_redirect(self):
        req = HttpRequest()
        req.method = 'GET'
        req.user = self.advisor_mack
        req.follow = True
        response = schedule_list(req)
        self.assertTrue(reverse('advisor-schedule-list') in response.url)

