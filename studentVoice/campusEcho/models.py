from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

class UserManager(BaseUserManager):
    def create_user(self, email, user_type='student', password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not user_type:
            raise ValueError('Users must have a user type')
        user = self.model(email=self.normalize_email(email), user_type=user_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password=None, **extra_fields):
            extra_fields.setdefault('user_type', 'administrator')
            extra_fields.setdefault('is_staff', True)
            extra_fields.setdefault('is_superuser', True)  # Ensure is_superuser is True
            if extra_fields.get('is_superuser') is not True:
                raise ValueError('Superuser must have is_superuser=True.')  # Raise error if is_superuser is not True
            return self.create_user(email, password=password, **extra_fields)



class User(AbstractBaseUser):
    
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('administrator', 'Administrator'),
    )
    
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    user_type = models.CharField(max_length=30, choices=USER_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Add this field for staff status
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_type', 'first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.email





class Profile(models.Model):
    FACULTY_CHOICES = [
        ('Medicine', 'Medicine'),
        ('Engineering', 'Engineering'),
        ('Media', 'Media'),
        ('Computing', 'Computing'),
        ('Business', 'Business'),
        ('Science and Technology', 'Science and Technology'),
        ('TVET', 'TVET'),
    ]

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message="Phone number must be in the format: '+1234567890'. Up to 15 digits allowed."
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    admission = models.CharField(max_length=50)  # Consider using DateField or IntegerField
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True)
    faculty = models.CharField(max_length=100, choices=FACULTY_CHOICES, blank=True, default='other')
    department = models.CharField(max_length=20, blank=True)  # Follow snake_case convention
    course = models.CharField(max_length=15, blank=True)
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=12, 
        blank=True, 
        help_text="Phone number must be in the format: '+1234567890'. Up to 15 digits allowed."
    )
    address = models.CharField(max_length=200, blank=True)
   
    def __str__(self):
        return self.user.username



class Feedback(models.Model):
    CATEGORY_CHOICES = [
        ('academics', 'Academics'),
        ('finance', 'Finance'),
        ('health', 'Health and Welfare'),
        ('housing', 'Housing'),
        ('other', 'Other'),
    ]
    
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('urgent', 'Urgent'),
        ('emergency', 'Emergency'),
        ('normal', 'Normal'),
    ]
    
    FEEDBACK_TYPE_CHOICES = [
        ('complaint', 'Complaint'),
        ('recommendation', 'Recommendation'),
        ('report', 'Report'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('resolved', 'Resolved'),
        ('pending', 'Pending'),
    ]

    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    severity = models.CharField(max_length=100, choices=SEVERITY_CHOICES)
    feedback_type = models.CharField(max_length=100, choices=FEEDBACK_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    evidence = models.ImageField(upload_to='feedback_evidence/', blank=True, null=True)
    recommendation = models.TextField(blank=True, null=True)    
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='pending')
    solution = models.TextField(blank=True, null=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return f"{self.get_category_display()} Feedback - {self.title}"
