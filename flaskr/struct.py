import enum

class AccountType(enum.Enum):
    Patient = 'patient'
    Doctor = 'doctor'
    Pharmacy = 'pharmacy'
    SuperUser = 'super_user'

class ReportType(enum.Enum):
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'

class PaymentStatus(enum.Enum):
    PAID = 'paid'
    PENDING = 'pending'

class AppointmentStatus(enum.Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'

class ExerciseStatus(enum.Enum):
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'

class PrescriptionStatus(enum.Enum):
    PAID = 'paid'
    UNPAID = 'unpaid'