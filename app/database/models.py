from sqlalchemy import (
    Column, Integer, String, Date, Boolean, ForeignKey,
    Text, DECIMAL, TIMESTAMP, UniqueConstraint, Index, Enum,
    DateTime, CheckConstraint,Time
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from sqlalchemy.sql import func

Base = declarative_base()

# ====================== Reusable Enums ======================
InstituteStatus = Enum("active", "inactive", "archived", name="institute_status")
AcademicYearStatus = Enum("planned", "active", "completed", name="academic_year_status")
StudentStatus = Enum("active", "inactive", "graduated", "suspended", name="student_status")
EnrollmentStatus = Enum("active", "completed", "cancelled", name="enrollment_status")
EmployeeStatus = Enum("active", "inactive", "terminated", name="employee_status")
HostelAllocationStatus = Enum("active", "vacated", "cancelled", name="hostel_status")
FeeStatus = Enum("pending", "partial", "paid", "overdue", name="fee_status")
PaymentStatus = Enum("success", "failed", "pending", name="payment_status")
AcademicMode = Enum("year", "semester", name="academic_mode")
AttendanceStatus = Enum( "present", "absent", "late", "excused", "half_day",name="attendance_status")



class Institute(Base):
    __tablename__ = "institutes"

    institute_id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)

    code = Column(String, unique=True, nullable=False)

    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    address = Column(JSONB, nullable=True)

    status = Column(
        InstituteStatus,
        nullable=False,
        server_default="active"
    )

    academic_structure = Column(String, nullable=True)

    academic_mode = Column(
        AcademicMode,
        nullable=False
    )

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_active = Column(Boolean, default=True)

    academic_years = relationship(
        "AcademicYear",
        back_populates="institute",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    students = relationship(
        "Student",
        back_populates="institute",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    employees = relationship(
        "Employee",
        back_populates="institute",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    standards = relationship(
        "Standard",
        back_populates="institute",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    subjects = relationship(
        "Subject",
        back_populates="institute",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    parents = relationship(
        "Parent",
        back_populates="institute",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    hostels = relationship(
        "Hostel",
        back_populates="institute",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    users = relationship(
        "User",
        back_populates="institute",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    roles = relationship(
        "Role",
        back_populates="institute",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint("char_length(code) > 0", name="check_code_not_empty"),

        Index("idx_institutes_code", "code"),
        Index("idx_institutes_status", "status"),
    )

    def __repr__(self):
        return f"<Institute(id={self.institute_id}, code='{self.code}')>"





class AcademicYear(Base):
    __tablename__ = "academic_years"

    academic_year_id = Column(Integer, primary_key=True)

    institute_id = Column(
        Integer,
        ForeignKey("institutes.institute_id", ondelete="CASCADE"),
        nullable=False
    )

    name = Column(String, nullable=False)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    is_current = Column(Boolean, default=False, nullable=False)

    status = Column(
        AcademicYearStatus,
        nullable=False,
        server_default="planned"
    )

   
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    institute = relationship(
        "Institute",
        back_populates="academic_years",
        passive_deletes=True
    )

    semesters = relationship(
        "Semester",
        back_populates="academic_year",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    sections = relationship(
        "Section",
        back_populates="academic_year",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    enrollments = relationship(
        "StudentEnrollment",
        back_populates="academic_year",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    fees = relationship(
        "Fee",
        back_populates="academic_year",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    hostel_allocations = relationship(
        "HostelAllocation",
        back_populates="academic_year",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint("end_date > start_date", name="check_valid_date_range"),

        UniqueConstraint(
            "institute_id",
            "name",
            name="uq_academic_year_name_per_institute"
        ),

        Index("idx_academic_years_institute", "institute_id"),
        Index("idx_academic_years_current", "institute_id", "is_current"),
    )

    def __repr__(self):
        return f"<AcademicYear(id={self.academic_year_id}, name='{self.name}')>"





class Semester(Base):
    __tablename__ = "semesters"

    semester_id = Column(Integer, primary_key=True)

    academic_year_id = Column(
        Integer,
        ForeignKey("academic_years.academic_year_id", ondelete="CASCADE"),
        nullable=False
    )

    name = Column(String, nullable=False)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    academic_year = relationship(
        "AcademicYear",
        back_populates="semesters",
        passive_deletes=True
    )

    sections = relationship(
        "Section",
        back_populates="semester",
        passive_deletes=True
    )

    subjects = relationship(
        "Subject",
        back_populates="semester",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    fees = relationship(
        "Fee",
        back_populates="semester",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint("end_date > start_date", name="check_semester_date_range"),

        UniqueConstraint(
            "academic_year_id",
            "name",
            name="uq_semester_name_per_year"
        ),

        Index("idx_semesters_academic_year", "academic_year_id"),
    )

    def __repr__(self):
        return f"<Semester(id={self.semester_id}, name='{self.name}')>"



class Standard(Base):
    __tablename__ = "standards"

    standard_id = Column(Integer, primary_key=True)

    institute_id = Column(
        Integer,
        ForeignKey("institutes.institute_id", ondelete="CASCADE"),
        nullable=False
    )

    name = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_active = Column(Boolean, default=True)
    institute = relationship(
        "Institute",
        back_populates="standards",
        passive_deletes=True
    )

    sections = relationship(
        "Section",
        back_populates="standard",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    subjects = relationship(
        "Subject",
        back_populates="standard",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    fees = relationship(
        "Fee",
        back_populates="standard",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    fee_components = relationship(
        "FeeComponent",
        back_populates="standard",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint("char_length(name) > 0", name="check_standard_name_not_empty"),

        UniqueConstraint(
            "institute_id",
            "name",
            name="uq_standard_name_per_institute"
        ),

        Index("idx_standards_institute", "institute_id"),
    )

    def __repr__(self):
        return f"<Standard(id={self.standard_id}, name='{self.name}')>"




class Section(Base):
    __tablename__ = "sections"

    section_id = Column(Integer, primary_key=True)

    standard_id = Column(
        Integer,
        ForeignKey("standards.standard_id", ondelete="CASCADE"),
        nullable=False
    )

    academic_year_id = Column(
        Integer,
        ForeignKey("academic_years.academic_year_id", ondelete="CASCADE"),
        nullable=False
    )

    semester_id = Column(
        Integer,
        ForeignKey("semesters.semester_id", ondelete="SET NULL"),
        nullable=True
    )

    name = Column(String, nullable=False)

    capacity = Column(Integer, nullable=False, default=40)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    standard = relationship(
        "Standard",
        back_populates="sections",
        passive_deletes=True
    )

    academic_year = relationship(
        "AcademicYear",
        back_populates="sections",
        passive_deletes=True
    )

    semester = relationship(
        "Semester",
        back_populates="sections",
        passive_deletes=True
    )

    enrollments = relationship(
        "StudentEnrollment",
        back_populates="section",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint("capacity > 0", name="check_capacity_positive"),
        UniqueConstraint(
            "standard_id",
            "academic_year_id",
            "semester_id",
            "name",
            name="uq_section_per_standard_year_semester"
        ),
        Index("idx_sections_standard_year", "standard_id", "academic_year_id"),
        Index("idx_sections_semester", "semester_id"),
    )

    def __repr__(self):
        return f"<Section(id={self.section_id}, name='{self.name}')>"




class Subject(Base):
    __tablename__ = "subjects"

    subject_id = Column(Integer, primary_key=True)

    institute_id = Column(
        Integer,
        ForeignKey("institutes.institute_id", ondelete="CASCADE"),
        nullable=False
    )

    standard_id = Column(
        Integer,
        ForeignKey("standards.standard_id", ondelete="CASCADE"),
        nullable=True
    )

    academic_year_id = Column(
        Integer,
        ForeignKey("academic_years.academic_year_id", ondelete="SET NULL"),
        nullable=True
    )

    semester_id = Column(
        Integer,
        ForeignKey("semesters.semester_id", ondelete="SET NULL"),
        nullable=True
    )

    name = Column(String, nullable=False)
    description = Column(JSONB, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_active = Column(Boolean, default=True)

    institute = relationship(
        "Institute",
        back_populates="subjects",
        passive_deletes=True
    )

    standard = relationship(
        "Standard",
        back_populates="subjects",
        passive_deletes=True
    )

    academic_year = relationship(
        "AcademicYear",
        passive_deletes=True
    )

    semester = relationship(
        "Semester",
        back_populates="subjects",
        passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint("char_length(name) > 0", name="check_subject_name_not_empty"),
        CheckConstraint(
            "(standard_id IS NOT NULL OR academic_year_id IS NOT NULL OR semester_id IS NOT NULL)",
            name="check_subject_scope_not_null"
        ),

        Index("idx_subjects_institute", "institute_id"),
        Index("idx_subjects_standard", "standard_id"),
        Index("idx_subjects_year", "academic_year_id"),
        Index("idx_subjects_semester", "semester_id"),
        UniqueConstraint(
            "institute_id",
            "standard_id",
            "academic_year_id",
            "semester_id",
            "name",
            name="uq_subject_scope_unique"
        ),
    )

    def __repr__(self):
        return f"<Subject(id={self.subject_id}, name='{self.name}')>"




class Student(Base):
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True)

    institute_id = Column(
        Integer,
        ForeignKey("institutes.institute_id", ondelete="CASCADE"),
        nullable=False
    )

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    dob = Column(Date, nullable=True)

    gender = Column(String, nullable=True)

    admission_year = Column(Integer, nullable=True)

    status = Column(
        StudentStatus,
        nullable=False,
        server_default=StudentStatus.ACTIVE.value
    )

    address = Column(JSONB, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_active = Column(Boolean, default=True)

    institute = relationship(
        "Institute",
        back_populates="students",
        passive_deletes=True
    )

    enrollments = relationship(
        "StudentEnrollment",
        back_populates="student",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    fees = relationship(
        "Fee",
        back_populates="student",
        passive_deletes=True
    )

    payments = relationship(
        "FeePayment",
        back_populates="student",
        passive_deletes=True
    )

    hostel_allocations = relationship(
        "HostelAllocation",
        back_populates="student",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    parents = relationship(
        "ParentStudent",
        back_populates="student",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint("char_length(first_name) > 0", name="check_first_name_not_empty"),
        CheckConstraint("char_length(last_name) > 0", name="check_last_name_not_empty"),
        CheckConstraint("dob IS NULL OR dob < CURRENT_DATE", name="check_valid_dob"),
        Index("idx_students_institute", "institute_id"),
        Index("idx_students_name", "first_name", "last_name"),
    )

    def __repr__(self):
        return f"<Student(id={self.student_id}, name='{self.first_name} {self.last_name}')>"




class StudentEnrollment(Base):
    __tablename__ = "student_enrollments"

    enrollment_id = Column(Integer, primary_key=True)

    student_id = Column(
        Integer,
        ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False
    )

    section_id = Column(
        Integer,
        ForeignKey("sections.section_id", ondelete="CASCADE"),
        nullable=False
    )

    academic_year_id = Column(
        Integer,
        ForeignKey("academic_years.academic_year_id", ondelete="CASCADE"),
        nullable=False
    )

    institute_id = Column(
        Integer,
        ForeignKey("institutes.institute_id", ondelete="CASCADE"),
        nullable=False
    )

    roll_number = Column(String, nullable=True)

    registration_number = Column(String, nullable=True)

    status = Column(
        EnrollmentStatus,
        nullable=False,
        server_default=EnrollmentStatus.ACTIVE.value
    )


    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    student = relationship(
        "Student",
        back_populates="enrollments",
        passive_deletes=True
    )

    section = relationship(
        "Section",
        back_populates="enrollments",
        passive_deletes=True
    )

    academic_year = relationship(
        "AcademicYear",
        back_populates="enrollments",
        passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint(
            "roll_number IS NULL OR char_length(roll_number) > 0",
            name="check_roll_not_empty"
        ),

        UniqueConstraint(
            "student_id",
            "academic_year_id",
            name="uq_student_enrollment_per_year"
        ),

        UniqueConstraint(
            "section_id",
            "roll_number",
            name="uq_roll_per_section"
        ),

        UniqueConstraint(
            "institute_id",
            "registration_number",
            name="uq_registration_number_per_institute"
        ),

        Index("idx_enroll_student", "student_id"),
        Index("idx_enroll_section", "section_id"),
        Index("idx_enroll_year", "academic_year_id"),
        Index("idx_enroll_student_year", "student_id", "academic_year_id"),
    )

    def __repr__(self):
        return f"<Enrollment(id={self.enrollment_id}, student={self.student_id})>"



class Parent(Base):
    __tablename__ = "parents"

    parent_id = Column(Integer, primary_key=True)

    institute_id = Column(
        Integer,
        ForeignKey("institutes.institute_id", ondelete="CASCADE"),
        nullable=False
    )

    name = Column(String, nullable=False)

    relation = Column(String, nullable=False)  
    # e.g., FATHER, MOTHER, GUARDIAN

    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)

    address = Column(JSONB, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_active = Column(Boolean, default=True)

    institute = relationship(
        "Institute",
        back_populates="parents",
        passive_deletes=True
    )

    students = relationship(
        "ParentStudent",
        back_populates="parent",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint("char_length(name) > 0", name="check_parent_name_not_empty"),

        Index("idx_parent_institute", "institute_id"),
        Index("idx_parent_phone", "phone"),
    )

    def __repr__(self):
        return f"<Parent(id={self.parent_id}, name='{self.name}')>"




class ParentStudent(Base):
    __tablename__ = "parent_students"

    id = Column(Integer, primary_key=True)

    parent_id = Column(
        Integer,
        ForeignKey("parents.parent_id", ondelete="CASCADE"),
        nullable=False
    )

    student_id = Column(
        Integer,
        ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False
    )

    relation = Column(String, nullable=False)  

    is_primary = Column(Boolean, default=False)  

    created_at = Column(DateTime, server_default=func.now())

    parent = relationship(
        "Parent",
        back_populates="students",
        passive_deletes=True
    )

    student = relationship(
        "Student",
        back_populates="parents",
        passive_deletes=True
    )

    __table_args__ = (
        UniqueConstraint(
            "parent_id",
            "student_id",
            name="uq_parent_student"
        ),

        CheckConstraint(
            "char_length(relation) > 0",
            name="check_relation_not_empty"
        ),

        Index("idx_ps_parent", "parent_id"),
        Index("idx_ps_student", "student_id"),
    )

    def __repr__(self):
        return f"<ParentStudent(parent={self.parent_id}, student={self.student_id})>"



class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True)

    institute_id = Column(
        Integer,
        ForeignKey("institutes.institute_id", ondelete="CASCADE"),
        nullable=False
    )

    name = Column(String, nullable=False)

    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    joining_date = Column(Date, nullable=True)

    status = Column(
        EmployeeStatus,
        nullable=False,
        server_default=EmployeeStatus.ACTIVE.value
    )

 
    employee_code = Column(String, nullable=True)  # unique per institute
    designation = Column(String, nullable=True)    # Teacher, Admin, etc.

 
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_active = Column(Boolean, default=True)


    institute = relationship(
        "Institute",
        back_populates="employees",
        passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint("char_length(name) > 0", name="check_employee_name_not_empty"),
        UniqueConstraint(
            "institute_id",
            "employee_code",
            name="uq_employee_code_per_institute"
        ),

        UniqueConstraint(
            "institute_id",
            "email",
            name="uq_employee_email_per_institute"
        ),

        Index("idx_employee_institute", "institute_id"),
        Index("idx_employee_email", "email"),
        Index("idx_employee_phone", "phone"),
    )

    def __repr__(self):
        return f"<Employee(id={self.employee_id}, name='{self.name}')>"





class Hostel(Base):
    __tablename__ = "hostels"

    hostel_id = Column(Integer, primary_key=True)

    institute_id = Column(
        Integer,
        ForeignKey("institutes.institute_id", ondelete="CASCADE"),
        nullable=False
    )

    name = Column(String, nullable=False)
    type = Column(String, nullable=True)  

    capacity = Column(Integer, nullable=True)

    address = Column(JSONB, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_active = Column(Boolean, default=True)

    institute = relationship(
        "Institute",
        back_populates="hostels",
        passive_deletes=True
    )

    rooms = relationship(
        "HostelRoom",
        back_populates="hostel",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint("char_length(name) > 0", name="check_hostel_name_not_empty"),

        CheckConstraint("capacity IS NULL OR capacity >= 0", name="check_hostel_capacity"),

        UniqueConstraint(
            "institute_id",
            "name",
            name="uq_hostel_name_per_institute"
        ),

        Index("idx_hostel_institute", "institute_id"),
    )

    def __repr__(self):
        return f"<Hostel(id={self.hostel_id}, name='{self.name}')>"



class HostelAllocation(Base):
    __tablename__ = "hostel_allocations"

    allocation_id = Column(Integer, primary_key=True)

    student_id = Column(
        Integer,
        ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False
    )

    room_id = Column(
        Integer,
        ForeignKey("hostel_rooms.room_id", ondelete="CASCADE"),
        nullable=False
    )

    academic_year_id = Column(
        Integer,
        ForeignKey("academic_years.academic_year_id", ondelete="CASCADE"),
        nullable=False
    )

    bed_number = Column(String, nullable=True)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)

    status = Column(
        HostelAllocationStatus,
        nullable=False,
        server_default=HostelAllocationStatus.ACTIVE.value
    )

    created_at = Column(DateTime, server_default=func.now())

    student = relationship(
        "Student",
        back_populates="hostel_allocations",
        passive_deletes=True
    )

    room = relationship(
        "HostelRoom",
        back_populates="allocations",
        passive_deletes=True
    )

    academic_year = relationship(
        "AcademicYear",
        back_populates="hostel_allocations",
        passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint(
            "end_date IS NULL OR end_date >= start_date",
            name="check_valid_date_range"
        ),

        CheckConstraint(
            "bed_number IS NULL OR char_length(bed_number) > 0",
            name="check_bed_not_empty"
        ),

        UniqueConstraint(
            "student_id",
            "academic_year_id",
            name="uq_student_hostel_per_year"
        ),

        Index("idx_alloc_student", "student_id"),
        Index("idx_alloc_room", "room_id"),
        Index("idx_alloc_year", "academic_year_id"),
    )

    def __repr__(self):
        return f"<HostelAllocation(student={self.student_id}, room={self.room_id})>"


# ====================== Fee System ======================


class Fee(Base):
    __tablename__ = "fees"

    fee_id = Column(Integer, primary_key=True)

    student_id = Column(
        Integer,
        ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False
    )

    academic_year_id = Column(
        Integer,
        ForeignKey("academic_years.academic_year_id", ondelete="CASCADE"),
        nullable=False
    )

    semester_id = Column(
        Integer,
        ForeignKey("semesters.semester_id", ondelete="SET NULL"),
        nullable=True
    )

    standard_id = Column(
        Integer,
        ForeignKey("standards.standard_id", ondelete="SET NULL"),
        nullable=True
    )

    fee_type = Column(String, nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    discount_amount = Column(DECIMAL(10, 2), default=0)
    paid_amount = Column(DECIMAL(10, 2), default=0)

    final_amount = Column(DECIMAL(10, 2), nullable=False)

    status = Column(
        FeeStatus,
        nullable=False,
        server_default=FeeStatus.PENDING.value
    )

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    student = relationship("Student", back_populates="fees", passive_deletes=True)

    academic_year = relationship("AcademicYear", back_populates="fees", passive_deletes=True)

    semester = relationship("Semester", back_populates="fees", passive_deletes=True)

    standard = relationship("Standard", back_populates="fees", passive_deletes=True)

    components = relationship(
        "FeeComponent",
        back_populates="fee",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    payments = relationship(
        "FeePayment",
        back_populates="fee",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="check_total_amount_positive"),
        CheckConstraint("discount_amount >= 0", name="check_discount_positive"),
        CheckConstraint("paid_amount >= 0", name="check_paid_positive"),
        CheckConstraint(
            "discount_amount <= total_amount",
            name="check_discount_not_exceed_total"
        ),
        CheckConstraint(
            "paid_amount <= final_amount",
            name="check_paid_not_exceed_final"
        ),
        CheckConstraint(
            "final_amount = total_amount - discount_amount",
            name="check_final_amount_correct"
        ),
        UniqueConstraint(
            "student_id",
            "academic_year_id",
            "semester_id",
            "fee_type",
            name="uq_fee_per_student_period_type"
        ),
        Index("idx_fee_student", "student_id"),
        Index("idx_fee_year", "academic_year_id"),
        Index("idx_fee_status", "status"),
    )

    def __repr__(self):
        return f"<Fee(id={self.fee_id}, student={self.student_id}, final={self.final_amount})>"


class FeeStructureComponent(Base):
    __tablename__ = "fee_structure_components"

    component_id = Column(Integer, primary_key=True)

    institute_id = Column(
        Integer,
        ForeignKey("institutes.institute_id", ondelete="CASCADE"),
        nullable=False
    )

    standard_id = Column(
        Integer,
        ForeignKey("standards.standard_id", ondelete="CASCADE"),
        nullable=False
    )

    name = Column(String, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)

    is_mandatory = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "standard_id",
            "name",
            name="uq_component_per_standard"
        ),
    )


class FeeComponent(Base):
    __tablename__ = "fee_components"

    component_id = Column(Integer, primary_key=True)

    fee_id = Column(
        Integer,
        ForeignKey("fees.fee_id", ondelete="CASCADE"),
        nullable=False
    )

    name = Column(String, nullable=False)

    amount = Column(DECIMAL(10, 2), nullable=False)

    created_at = Column(DateTime, server_default=func.now())

    fee = relationship(
        "Fee",
        back_populates="components",
        passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint("amount >= 0", name="check_component_amount_positive"),

        Index("idx_fee_component_fee", "fee_id"),
    )






class FeePayment(Base):
    __tablename__ = "fee_payments"

    payment_id = Column(Integer, primary_key=True)

    fee_id = Column(
        Integer,
        ForeignKey("fees.fee_id", ondelete="CASCADE"),
        nullable=False
    )

    amount = Column(DECIMAL(10, 2), nullable=False)

    payment_method = Column(String, nullable=True)

    transaction_id = Column(String, nullable=True)
    receipt_number = Column(String, nullable=False)

    remarks = Column(Text, nullable=True)

    payment_date = Column(DateTime, server_default=func.now())

    status = Column(
        PaymentStatus,
        nullable=False,
        server_default=PaymentStatus.SUCCESS.value
    )
    created_at = Column(DateTime, server_default=func.now())
    fee = relationship(
        "Fee",
        back_populates="payments",
        passive_deletes=True
    )

    documents = relationship(
        "FeePaymentDocument",
        back_populates="payment",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_payment_amount_positive"),
        UniqueConstraint(
            "receipt_number",
            name="uq_receipt_number"
        ),
        UniqueConstraint(
            "transaction_id",
            name="uq_transaction_id"
        ),

        Index("idx_payment_fee", "fee_id"),
        Index("idx_payment_date", "payment_date"),
    )

    def __repr__(self):
        return f"<Payment(id={self.payment_id}, amount={self.amount})>"


class FeePaymentDocument(Base):
    __tablename__ = "fee_payment_documents"

    document_id = Column(Integer, primary_key=True)

    payment_id = Column(
        Integer,
        ForeignKey("fee_payments.payment_id", ondelete="CASCADE"),
        nullable=False
    )

    file_url = Column(String, nullable=False)
    file_type = Column(String, nullable=True)

    uploaded_at = Column(DateTime, server_default=func.now())

    payment = relationship(
        "FeePayment",
        back_populates="documents",
        passive_deletes=True
    )

    __table_args__ = (
        Index("idx_payment_doc_payment", "payment_id"),
    )


# ====================== User & RBAC ======================
# user_rbac_models.py

from sqlalchemy import (
    Column, Integer, String, ForeignKey,
    Index, UniqueConstraint, CheckConstraint,
    Boolean, DateTime
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# -------------------- USER --------------------

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)

    institute_id = Column(
        Integer,
        ForeignKey("institutes.institute_id", ondelete="CASCADE"),
        nullable=False
    )

    aadhar_number = Column(String, nullable=True)

    username = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)

    # Link to only ONE entity
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="SET NULL"), nullable=True)
    parent_id = Column(Integer, ForeignKey("parents.parent_id", ondelete="SET NULL"), nullable=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="SET NULL"), nullable=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    institute = relationship("Institute", back_populates="users", passive_deletes=True)

    student = relationship("Student", passive_deletes=True)
    parent = relationship("Parent", passive_deletes=True)
    employee = relationship("Employee", passive_deletes=True)

    roles = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    __table_args__ = (
        UniqueConstraint("institute_id", "username", name="uq_username_per_institute"),
        UniqueConstraint("institute_id", "aadhar_number", name="uq_aadhar_per_institute"),
        CheckConstraint(
            """
            (student_id IS NOT NULL)::int +
            (parent_id IS NOT NULL)::int +
            (employee_id IS NOT NULL)::int <= 1
            """,
            name="check_single_user_identity"
        ),

        Index("idx_users_institute_id", "institute_id"),
    )

# -------------------- ROLE --------------------

class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True)

    institute_id = Column(
        Integer,
        ForeignKey("institutes.institute_id", ondelete="CASCADE"),
        nullable=False
    )

    name = Column(String, nullable=False)
    description = Column(String)

    created_at = Column(DateTime, server_default=func.now())

    institute = relationship("Institute", back_populates="roles", passive_deletes=True)

    role_permissions = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    user_roles = relationship(
        "UserRole",
        back_populates="role",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    __table_args__ = (
        UniqueConstraint("institute_id", "name", name="uq_role_name_per_institute"),
        Index("idx_roles_institute_id", "institute_id"),
    )

# -------------------- PERMISSION --------------------

class Permission(Base):
    __tablename__ = "permissions"

    permission_id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)
    module = Column(String, nullable=True)
    description = Column(String)

    role_permissions = relationship(
        "RolePermission",
        back_populates="permission",
        passive_deletes=True
    )

# -------------------- ROLE PERMISSION --------------------

class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True)

    role_id = Column(
        Integer,
        ForeignKey("roles.role_id", ondelete="CASCADE"),
        nullable=False
    )

    permission_id = Column(
        Integer,
        ForeignKey("permissions.permission_id", ondelete="CASCADE"),
        nullable=False
    )

    role = relationship("Role", back_populates="role_permissions", passive_deletes=True)
    permission = relationship("Permission", back_populates="role_permissions", passive_deletes=True)

    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )

# -------------------- USER ROLE --------------------

class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False
    )

    role_id = Column(
        Integer,
        ForeignKey("roles.role_id", ondelete="CASCADE"),
        nullable=False
    )

    user = relationship("User", back_populates="roles", passive_deletes=True)
    role = relationship("Role", back_populates="user_roles", passive_deletes=True)

    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_role"),
    )


class Timetable(Base):
    __tablename__ = "timetables"

    timetable_id = Column(Integer, primary_key=True)

    institute_id = Column(Integer, ForeignKey("institutes.institute_id", ondelete="CASCADE"), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("academic_years.academic_year_id", ondelete="CASCADE"), nullable=False)
    semester_id = Column(Integer, ForeignKey("semesters.semester_id", ondelete="SET NULL"))

    section_id = Column(Integer, ForeignKey("sections.section_id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id", ondelete="CASCADE"), nullable=False)

    day_of_week = Column(Enum(
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday",
        name="day_of_week"
    ), nullable=False)

    period_number = Column(Integer, nullable=False)

    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    employee_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="SET NULL"))

    __table_args__ = (
        Index("idx_timetable_section_day", "section_id", "day_of_week"),
        Index("idx_timetable_academic_year", "academic_year_id"),

        UniqueConstraint(
            "section_id", "academic_year_id", "day_of_week", "period_number",
            name="uq_timetable_slot_per_section"
        ),

        UniqueConstraint(
            "employee_id", "day_of_week", "period_number", "academic_year_id",
            name="uq_teacher_schedule_conflict"
        ),

        CheckConstraint("start_time < end_time", name="check_valid_time_range"),
        CheckConstraint("period_number > 0 AND period_number <= 12", name="check_valid_period"),
    )