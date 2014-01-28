############################
Student Data
############################

You can access data about the students who are enrolled in your course at any time after you create the course. 

For information about the data you can access, see the following topics:

* :ref:`PII`

* :ref:`Accessing_student_data`

* :ref:`Accessing_anonymized`


.. _PII:

***************************************************************
Guidance for working with personal information
***************************************************************

The information that edX collects from site registrants includes personal information that can be used to identify, contact, and locate individuals. This information is available to course authors for the students who are enrolled in their courses. 

Course authors should/must/are obligated to/? treat this information... 

**Question**: what suggestions can/should be made?

.. _Accessing_student_data:

****************************
Accessing student data
****************************

You can view data about the students who are currently enrolled in your course. Data for enrolled students is also available for download in CSV (comma-separated value) format.  

======================
Student-reported data
======================

When students register with edX, they select a public username and supply information about themselves. 

 .. image:: Images/Registration_page.png
   :alt: Fields that collect student information during registration

Students then register for as many individual courses as they choose, which enrolls them in the selected courses. 

You can access this self-reported information for all of the students who are enrolled in your course:

* username
* name
* email
* year_of_birth
* gender
* level_of_education **Question**: do we need to decode the values stored for the drop-down choices?
* mailing_address
* goals

Students can register for your course throughout the enrollment period, and they can unregister from a course at any time, which unenrolls them from the course. Students can also change their email addresses and full names at any time. 
The student data that is available to course staff always reflects the set of live, current enrollments. 

***Question**: is this correct? 

==========================================
Viewing and downloading student data
==========================================

You can view and download student data to learn about population demographics at a specific point in time, compare demographics at different points in time, and learn about trends in the population over time.

**Important**: The larger the enrollment for your course, the longer it takes to create and download this file. Do not navigate away from this page while you wait. **Question:** Is this correct?

To view or download student data:

#. View the live version of your course.

#. Click **Instructor Dashboard** then **Try New Beta Dashboard**.

#. Click **Data Download**.

#. To display student enrollment data, click **List enrolled students' profile information**.

   A table of the student data displays, with one row for each enrolled student. Longer values, such as student goals, are truncated.

  .. image:: Images/StudentData_Table.png
    :alt: Table with columns for the collected data points and rows for each student on the Instructor Dashboard

   **Note**:: In the future, edX may also request that students select a language and location. This data is not collected at this time.

5. To download student enrollment data in a CSV file, click **Download profile information as a CSV**.

   You are prompted to open or save the enrolled_profiles.csv file. All student-supplied data is included without truncation.

**Note**:: In addition to the data for enrolled students, data for the course staff is included in the display or file.

==========================================
Viewing demographic distributions
==========================================

You can view a course-wide summary of certain demographic distributions for your currently enrolled students. The total count for each value reported for gender and educational attainment displays on the Instructor Dashboard. 

To display demographic distributions for gender and educational attainment:

#. View the live version of your course.

#. Click **Instructor Dashboard** then **Try New Beta Dashboard**.

#. Click **Analytics**. Tables display Gender Distribution and Level of Education for the students currently enrolled in your course.

   .. image:: Images/Distribution_Education.png
    :alt: Table with columns for different possible values reported for gender and total counts for each value

   .. image:: Images/Distribution_Gender.png
    :alt: Table with columns for different possible values reported for level of education completed and total counts for each value

Data for individual students is not shown, and you cannot download these counts directly from this page. See :ref:`Viewing and downloading student data`.

.. _Accessing_anonymized:

********************************
Accessing anonymized student IDs
********************************

Some of the tools that are available for use with the edX platform, including external graders and surveys, work with anonymized student data. If it becomes necessary to deanonymize previously anonymized data, you can download a CSV file to use for that purpose.

To download a file of assigned user IDs and anonymized user IDs:

#. View the live version of your course.

#. Click **Instructor Dashboard** > **Try New Beta Dashboard**.

#. Click **Data Download** > **Get Student Anonymized IDs CSV**.

You are prompted to open or save the (course-id)-anon-id.csv file for your course. This file contains the user ID that is assigned to each student at registration and its corresponding anonymized ID. Values are included for every student who ever enrolled for your course. 

You can use the data in this file, and join it with the data in the enrolled_profile.csv file of student data and any (course_id)_grade_report_(date).csv file for your course to research and deanonymize student data.



