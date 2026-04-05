from sqlalchemy import (
    Column, Integer, String, Date, Boolean, ForeignKey,
    Text, DECIMAL, Timestamp
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
    status = Column(String)
    academic_structure = Column(String)
    current_academic_year_id = Column(Integer, ForeignKey("academic_years.academic_year_id"))
    academic_mode = Column(String)  # year / semester
    created_at = Column(Timestamp, server_default=func.now())

    academic_years = relationship("AcademicYear", back_populates="institute")



class AcademicYear(Base):
    __tablename__ = "academic_years"

    academic_year_id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.institute_id"))
    name = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    is_current = Column(Boolean)

    institute = relationship("Institute", back_populates="academic_years")
    semesters = relationship("Semester", back_populates="academic_year")


class Semester(Base):
    __tablename__ = "semesters"

    semester_id = Column(Integer, primary_key=True)
    academic_year_id = Column(Integer, ForeignKey("academic_years.academic_year_id"))
    name = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)

    academic_year = relationship("AcademicYear", back_populates="semesters")


class Standard(Base):
    __tablename__ = "standards"

    standard_id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.institute_id"))
    name = Column(String)


class Section(Base):
    __tablename__ = "sections"

    section_id = Column(Integer, primary_key=True)
    standard_id = Column(Integer, ForeignKey("standards.standard_id"))
    academic_year_id = Column(Integer, ForeignKey("academic_years.academic_year_id"))
    semester_id = Column(Integer, ForeignKey("semesters.semester_id"), nullable=True)
    name = Column(String)
    capacity = Column(Integer)


class Subject(Base):
    __tablename__ = "subjects"

    subject_id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.institute_id"))
    standard_id = Column(Integer, ForeignKey("standards.standard_id"))
    academic_year_id = Column(Integer, ForeignKey("academic_years.academic_year_id"))
    semester_id = Column(Integer, ForeignKey("semesters.semester_id"), nullable=True)
    name = Column(String)
    description = Column(JSONB)



class Student(Base):
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.institute_id"))
    first_name = Column(String)
    last_name = Column(String)
    dob = Column(Date)
    gender = Column(String)
    admission_year = Column(Integer)
    status = Column(String)
    adress = Column(JSONB)
    created_at = Column(Timestamp, server_default=func.now())

    enrollments = relationship("StudentEnrollment", back_populates="student")


class StudentEnrollment(Base):
    __tablename__ = "student_enrollments"

    enrollment_id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.student_id"))
    section_id = Column(Integer, ForeignKey("sections.section_id"))
    academic_year_id = Column(Integer, ForeignKey("academic_years.academic_year_id"))
    roll_number = Column(String)
    registration_number = Column(String)
    status = Column(String)

    student = relationship("Student", back_populates="enrollments")


class Parent(Base):
    __tablename__ = "parents"

    parent_id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.institute_id"))
    father_name = Column(String)
    mother_name = Column(String)
    phone = Column(String)
    email = Column(String)
    address = Column(JSONB)


class ParentStudent(Base):
    __tablename__ = "parent_students"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("parents.parent_id"))
    student_id = Column(Integer, ForeignKey("students.student_id"))
    relation = Column(String)



class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.institute_id"))
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    role = Column(String)
    joining_date = Column(Date)
    status = Column(String)



class Hostel(Base):
    __tablename__ = "hostels"

    hostel_id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.institute_id"))
    name = Column(String)
    type = Column(String)
    capacity = Column(Integer)
    address = Column(JSONB)


class HostelRoom(Base):
    __tablename__ = "hostel_rooms"

    room_id = Column(Integer, primary_key=True)
    hostel_id = Column(Integer, ForeignKey("hostels.hostel_id"))
    room_number = Column(String)
    floor = Column(Integer)
    capacity = Column(Integer)
    occupied_count = Column(Integer)


class HostelAllocation(Base):
    __tablename__ = "hostel_allocations"

    allocation_id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.student_id"))
    room_id = Column(Integer, ForeignKey("hostel_rooms.room_id"))
    academic_year_id = Column(Integer, ForeignKey("academic_years.academic_year_id"))
    bed_number = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String)



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
    status = Column(String)

    created_at = Column(Timestamp, server_default=func.now())
    updated_at = Column(Timestamp, onupdate=func.now())

    payments = relationship("FeePayment", back_populates="fee")


class FeeComponent(Base):
    __tablename__ = "fee_components"

    component_id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.institute_id"))
    standard_id = Column(Integer, ForeignKey("standards.standard_id"), nullable=True)
    fee_id = Column(Integer, ForeignKey("fees.fee_id"), nullable=True)

    name = Column(String)
    description = Column(Text)
    amount = Column(DECIMAL)
    is_mandatory = Column(Boolean)

    created_at = Column(Timestamp, server_default=func.now())
    updated_at = Column(Timestamp, onupdate=func.now())



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
    status = Column(String)

    fee = relationship("Fee", back_populates="payments")
    documents = relationship("FeePaymentDocument", back_populates="payment")


class FeePaymentDocument(Base):
    __tablename__ = "fee_payment_documents"

    document_id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, ForeignKey("fee_payments.payment_id"))

    file_url = Column(String)
    file_type = Column(String)
    uploaded_at = Column(Timestamp, server_default=func.now())

    payment = relationship("FeePayment", back_populates="documents")



class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.institute_id"))
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=True)
    username = Column(String)
    password_hash = Column(String)
    role = Column(String)
    adhar_number = Column(String, unique=True, nullable=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=True)
    parent_id = Column(Integer, ForeignKey("parents.parent_id"), nullable=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=True)

    created_at = Column(Timestamp, server_default=func.now())