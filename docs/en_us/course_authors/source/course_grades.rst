############################
Grades
############################

You can review information about how grading is configured for your course, and generate student grades, at any time after you create the course. 

For information about the grading data you can access, see the following topics:

* :ref:`Reviewing_grades`

* :ref:`Accessing_grades`

* :ref:`Adjusting_grades`


.. _Reviewing_grades:

********************************************************
Reviewing how grading is configured for your course
********************************************************

You can review the assignment types that contribute to student grades and their respective weights, generate student grades, and download a file of the grades from the Instructor Dashboard.

You establish a grading policy for your course when you create it in Studio. While the course is running, you can view an XML representation of the assignment types in your course and how they are weighted to determine students' grades.

#. View the live version of your course.

#. Click **Instructor Dashboard** > **Try New Beta Dashboard**.

#. Click **Data Download** > **Grading Configuration**.
   A list of the assignment types in your course displays. In this example, Homework is weighted as 60% of the grade. 

   .. image:: Images/Grading_Configuration.png
     :alt: XML of course assignment types and weights for grading

   In Studio, you defined this information by selecting **Settings** > **Grading**.

   .. image:: Images/Grading_Configuration_Studio.png
     :alt: Studio example of homework assignment type and grading weight


.. _Accessing_grades:

********************************************************
Accessing student grades
********************************************************

You can generate and review your students' grades at any time during your course. You can generate grades for a single  student, who can be either currently enrolled or unenrolled, or for all currently enrolled students.

=========================================================
Generating grades for a single student
=========================================================

For a single student, you can review the assessment for every assignment and the overall total as of the current date.You identify the student by supplying either an email address or username. The student does not need to be enrolled in the course.

To view the current grading status for a specified student:

#. View the live version of your course.

#. Click **Instructor Dashboard** > **Try New Beta Dashboard**.

#. Click **Student Admin**.

#. In the Student-Specific Grade Inspection section, enter the student's email address or username.

#. Click **Student Progress Page**.
   A graph shows the percentage for each homework, lab, midterm, final, and any other assignment types in your course, and the total for the course to date. 

.. I'd like to include an image but don't have good sample data.

=========================================================
Generating grades for enrolled students
=========================================================

When you initiate calculations to grade student work, a process starts on the edX servers. The complexity of your grading configuration and the number of students enrolled in your course affect how long the process takes. You can  download a CSV (comma-separated value) file with the calculated grades when the grading process is complete. You cannot view student grades on the Instructor Dashboard. 

To generate grades for the students who are currently enrolled in your class:

#. View the live version of your course.

#. Click **Instructor Dashboard** > **Try New Beta Dashboard**.

#. Click **Data Download**.

#. To start the grading process, click **Generate Grade Report**.
   A status message indicates that grade report generation is in progress. When the file is ready for download, a link displays at the bottom of the page.

==========================================
Downloading grades for enrolled students
==========================================

After you request a grade report for your students, the result is a time-stamped CSV file that includes columns to identify each student: id, email, and username. It then includes a column for every assignment that is included in your grading configuration: each homework, lab, midterm, final, and any other assignment type you added to your course. 

**Question**: should more info be given on how grades are actually calculated, for example, the effect of the "droppable"
setting?

To download a file of student grades:

#. View the live version of your course.

#. Click **Instructor Dashboard** > **Try New Beta Dashboard**.

#. Click **Data Download**.

#. To open or save a grade report file, click the (course_id)_grade_report_(date).csv file name at the bottom of the page.

===================================================
Viewing student demographics for graded problems
===================================================

For a specified problem, you can view the grade distribution by **Question** what is the first graph supposed to plot? and by year of birth.

To display demographic distributions for gender and educational attainment:

#. View the live version of your course.

#. Click **Instructor Dashboard** > **Try New Beta Dashboard**.

#. Click **Analytics**. 

#. In the Grade Distribution section, select a problem. **Question**: how do they correlate the codes in this drop-down with actual constructed problems? 
   Graphs display how grades for that problem are distributed in the student population by **to come** and year of birth.

   .. image:: Images/Distribution_Grades.png
    :alt: 


.. _Adjusting_grades:

***********************************
Adjusting grades
***********************************

You can adjust grades for one student at a time, or for the entire course.




===================================================
Rescoring student submissions
===================================================

For a specified problem, you can rescore the work submitted by a single student, or rescore the submissions made by every enrolled student. 

**Question:** problem URLs - how do they get these? and, how differnt than the Problem drop-down on the Analytics tab?


===================================================
Resetting student attempts
===================================================

**Question**: what does resetting student attempts do?



