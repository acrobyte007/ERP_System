from sqlalchemy import (
    Column, Integer, String, Date, Boolean, ForeignKey,
    Text, DECIMAL, Timestamp,UniqueConstraint, Index,Enum
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func


Base = declarative_base()


class Institute(Base):
    __tablename__ = "institutes"

    institute_id = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String, unique=True)
    email = Column(String)
    phone = Column(String)
    address = Column(JSONB)
    status = Column(Enum("active", "inactive", "archived", name="institute_status"), nullable=False)
    academic_structure = Column(String)
    current_academic_year_id = Column(Integer, ForeignKey("academic_years.academic_year_id"))
    academic_mode = Column(String)  # year / semester
    created_at = Column(Timestamp, server_default=func.now())
    academic_years = relationship("AcademicYear", back_populates="institute")
    __table_args__=(
        Index("idx_institutes_code", "code"),
        Index("idx_institutes_status", "status")
    )



class AcademicYear(Base):
    __tablename__ = "academic_years"

    academic_year_id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.institute_id"),nullable=False)
    name = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    is_current = Column(Boolean)
    status = Column(Enum("planned", "active", "completed", name="academic_year_status"))
    institute = relationship("Institute", back_populates="academic_years")
    semesters = relationship("Semester", back_populates="academic_year")
    __table_args__=(
        Index("idx_academic_years_institute", "institute_id"),
        Index("idx_academic_years_current", "institute_id", "is_current"),
        Index("idx_academic_years_status", "status")
    )


class Semester(Base):
    __tablename__ = "semesters"

    semester_id = Column(Integer, primary_key=True)
    academic_year_id = Column(Integer, ForeignKey("academic_years.academic_year_id"))
    name = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    academic_year = relationship("AcademicYear", back_populates="semesters")
    __table_args__=(
        Index("idx_semesters_academic_year", "academic_year_id")
    )


class Standard(Base):
    __tablename__ = "standards"

    standard_id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.institute_id"), nullable=False)
    name = Column(String)
    __table_args__=(
        Index("idx_standards_institute", "institute_id")
    )



class Section(Base):
    __tablename__ = "sections"

    section_id = Column(Integer, primary_key=True)
    standard_id = Column(Integer, ForeignKey("standards.standard_id"))
    academic_year_id = Column(Integer, ForeignKey("academic_years.academic_year_id"))
    semester_id = Column(Integer, ForeignKey("semesters.semester_id"), nullable=True)
    name = Column(String)
    capacity = Column(Integer)

    __table_args__=(
        Index("idx_sections_standard", "standard_id"),
        Index("idx_sections_year", "academic_year_id"),
        Index("idx_sections_semester", "semester_id"),
        Index("idx_sections_std_year", "standard_id", "academic_year_id")
    )


class Subject(Base):
    __tablename__ = "subjects"

    subject_id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.institute_id"),nullable=False)
    standard_id = Column(Integer, ForeignKey("standards.standard_id"))
    academic_year_id = Column(Integer, ForeignKey("academic_years.academic_year_id"))
    semester_id = Column(Integer, ForeignKey("semesters.semester_id"), nullable=True)
    name = Column(String)
    description = Column(JSONB)

    __table_args__=(
        Index("idx_subjects_standard", "standard_id"),
        Index("idx_subjects_year", "academic_year_id"),
        Index("idx_subjects_semester", "semester_id"),
        Index("idx_subjects_institute", "institute_id")
    )



class Student(Base):
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.institute_id"), nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    dob = Column(Date)
    gender = Column(String)
    admission_year = Column(Integer)
    status = Column(Enum("active", "inactive", "graduated", "suspended", name="student_status"), nullable=False)
    address = Column(JSONB)
    created_at = Column(Timestamp, server_default=func.now())
    enrollments = relationship("StudentEnrollment", back_populates="student")
    __table_args__=(
        Index("idx_students_institute", "institute_id"),
        Index("idx_students_name", "first_name", "last_name"),
        Index("idx_students_status", "status")
    )


class StudentEnrollment(Base):
    __tablename__ = "student_enrollments"

    enrollment_id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.student_id"))
    section_id = Column(Integer, ForeignKey("sections.section_id"))
    academic_year_id = Column(Integer, ForeignKey("academic_years.academic_year_id"))
    roll_number = Column(String)
    registration_number = Column(String)
    status = Column(Enum("active", "completed", "cancelled", name="enrollment_status"), nullable=False)
    student = relationship("Student", back_populates="enrollments")

    __table_args__=(
        Index("idx_enroll_student", "student_id"),
        Index("idx_enroll_section", "section_id"),
        Index("idx_enroll_year", "academic_year_id"),
        Index("idx_enroll_student_year", "student_id", "academic_year_id")
    )


class Parent(Base):
    __tablename__ = "parents"

    parent_id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.institute_id"),nullable=False)
    father_name = Column(String)
    mother_name = Column(String)
    phone = Column(String)
    email = Column(String)
    address = Column(JSONB)

    __table_args__=(
        Index("idx_parents_institute", "institute_id"),
        Index("idx_parents_phone", "phone"),
    )


class ParentStudent(Base):
    __tablename__ = "parent_students"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("parents.parent_id"))
    student_id = Column(Integer, ForeignKey("students.student_id"))
    relation = Column(String)
    __table_args__=(
        Index("idx_parent_student_parent", "parent_id"),
        Index("idx_parent_student_student", "student_id")
    )



class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.institute_id"),nullable=False)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    role = Column(String)
    joining_date = Column(Date)
    status = Column(Enum("active", "inactive", "terminated", name="employee_status"), nullable=False)

    __table_args__=(
        Index("idx_employees_institute", "institute_id"),
        Index("idx_employees_role", "role"),
        Index("idx_employees_status", "status")
    )



class Hostel(Base):
    __tablename__ = "hostels"

    hostel_id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.institute_id"),nullable=False)
    name = Column(String)
    type = Column(String)
    capacity = Column(Integer)
    address = Column(JSONB)

    __table_args__=(
        Index("idx_hostels_institute", "institute_id")
    )


class HostelRoom(Base):
    __tablename__ = "hostel_rooms"

    room_id = Column(Integer, primary_key=True)
    hostel_id = Column(Integer, ForeignKey("hostels.hostel_id"))
    room_number = Column(String)
    floor = Column(Integer)
    capacity = Column(Integer)
    occupied_count = Column(Integer)
    __table_args__=(
        Index("idx_rooms_hostel", "hostel_id"),
        Index("idx_rooms_room_number", "room_number")
    )


class HostelAllocation(Base):
    __tablename__ = "hostel_allocations"

    allocation_id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.student_id"))
    room_id = Column(Integer, ForeignKey("hostel_rooms.room_id"))
    academic_year_id = Column(Integer, ForeignKey("academic_years.academic_year_id"))
    bed_number = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(Enum("active", "vacated", "cancelled", name="hostel_status"), nullable=False)
    __table_args__=(
        Index("idx_alloc_student", "student_id"),
        Index("idx_alloc_room", "room_id"),
        Index("idx_alloc_year", "academic_year_id"),
        Index("idx_alloc_student_year", "student_id", "academic_year_id")
    )



class Fee(Base):
    __tablename__ = "fees"

    fee_id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.student_id"))
    academic_year_id = Column(Integer, ForeignKey("academic_years.academic_year_id"))
    semester_id = Column(Integer, ForeignKey("semesters.semester_id"), nullable=True)
    standard_id = Column(Integer, ForeignKey("standards.standard_id"), nullable=True)
    fee_type = Column(String)
    discount_amount = Column(DECIMAL)
    final_amount = Column(DECIMAL)
    status = Column(Enum("pending", "partial", "paid", "overdue", name="fee_status"), nullable=False)
    created_at = Column(Timestamp, server_default=func.now())
    updated_at = Column(Timestamp, onupdate=func.now())
    payments = relationship("FeePayment", back_populates="fee")

    __table_args__=(
        Index("idx_fees_student", "student_id"),
        Index("idx_fees_year", "academic_year_id"),
        Index("idx_fees_status", "status"),
        Index("idx_fees_student_year", "student_id", "academic_year_id")
    )


class FeeComponent(Base):
    __tablename__ = "fee_components"

    component_id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.institute_id"),nullable=False)
    standard_id = Column(Integer, ForeignKey("standards.standard_id"), nullable=True)
    fee_id = Column(Integer, ForeignKey("fees.fee_id"), nullable=True)
    name = Column(String)
    description = Column(Text)
    amount = Column(DECIMAL)
    is_mandatory = Column(Boolean)
    created_at = Column(Timestamp, server_default=func.now())
    updated_at = Column(Timestamp, onupdate=func.now())
    __table_args__=(
        Index("idx_fee_comp_institute", "institute_id"),
        Index("idx_fee_comp_standard", "standard_id"),
        Index("idx_fee_comp_fee", "fee_id")
    )



class FeePayment(Base):
    __tablename__ = "fee_payments"

    payment_id = Column(Integer, primary_key=True)
    fee_id = Column(Integer, ForeignKey("fees.fee_id"))
    student_id = Column(Integer, ForeignKey("students.student_id"))
    amount = Column(DECIMAL)
    payment_method = Column(String)
    transaction_id = Column(String)
    receipt_number = Column(String)
    remarks = Column(Text)
    payment_date = Column(Timestamp)
    status = Column(Enum("success", "failed", "pending", name="payment_status"), nullable=False)
    fee = relationship("Fee", back_populates="payments")
    documents = relationship("FeePaymentDocument", back_populates="payment")
    __table_args__=(
        Index("idx_payments_fee", "fee_id"),
        Index("idx_payments_student", "student_id"),
        Index("idx_payments_date", "payment_date"),
        Index("idx_payments_status", "status")
    )



class FeePaymentDocument(Base):
    __tablename__ = "fee_payment_documents"

    document_id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, ForeignKey("fee_payments.payment_id"))
    file_url = Column(String)
    file_type = Column(String)
    uploaded_at = Column(Timestamp, server_default=func.now())
    payment = relationship("FeePayment", back_populates="documents")

    __table_args__=(
        Index("idx_docs_payment", "payment_id")
    )





class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.institute_id"), nullable=False)
    adhar_number = Column(String, unique=True, nullable=True)
    username = Column(String)
    password_hash = Column(String)

    role = Column(String)

    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=True)
    parent_id = Column(Integer, ForeignKey("parents.parent_id"), nullable=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=True)

    created_at = Column(Timestamp, server_default=func.now())

    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_users_institute_id", "institute_id"),
        Index("idx_users_username", "username"),
        Index("idx_users_student", "student_id"),
        Index("idx_users_parent", "parent_id"),
        Index("idx_users_employee", "employee_id")
    )


class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.institute_id"), nullable=False)

    name = Column(String, nullable=False)
    description = Column(String)

    created_at = Column(Timestamp, server_default=func.now())

    institute = relationship("Institute")
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_roles_institute_id", "institute_id"),
        Index("idx_roles_name", "name")
    )


class Permission(Base):
    __tablename__ = "permissions"

    permission_id = Column(Integer, primary_key=True)

    name = Column(String, unique=True, nullable=False)
    module = Column(String)
    description = Column(String)

    role_permissions = relationship("RolePermission", back_populates="permission")

    __table_args__ = (
        Index("idx_permissions_name", "name"),
        Index("idx_permissions_module", "module"),
    )


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True)

    role_id = Column(Integer, ForeignKey("roles.role_id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.permission_id"), nullable=False)

    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")

    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
        Index("idx_role_permissions_role_id", "role_id"),
        Index("idx_role_permissions_permission_id", "permission_id"),
    )


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.role_id"), nullable=False)
    user = relationship("User", back_populates="roles")

    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_role"),
        Index("idx_user_roles_user_id", "user_id"),
        Index("idx_user_roles_role_id", "role_id"),
    )