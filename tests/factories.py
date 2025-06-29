import factory
from factory.alchemy import SQLAlchemyModelFactory
from app.db.models import Employee, Transaction, Account
from app.core.security import get_password_hash

class EmployeeFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Employee
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker("name")
    email = factory.Sequence(lambda n: f"employee{n}@test.com")
    phone = factory.Faker("phone_number")
    role = "clerk"
    password_hash = factory.LazyFunction(lambda: get_password_hash("password123"))


class AccountFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Account
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    PID = factory.Sequence(lambda n: f"PID{n:05}")
    name = factory.Faker("name")
    email = factory.Sequence(lambda n: f"account{n}@test.com")
    phone = factory.Faker("phone_number")
    is_active = True
    balance = 1000.0


class TransactionFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Transaction
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    amount = 100.0
    type = "deposit"
    sender_id = None
    recv_id = factory.SubFactory(AccountFactory)
    timestamp = factory.Faker("date_time_this_year")
    reversed = False
