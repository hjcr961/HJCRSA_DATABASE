# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class MainMembers(models.Model):
    branch_member_number = models.CharField(max_length=255, null=True, blank=True, editable=False)
    card_number = models.IntegerField(db_column='Card_Number', primary_key=True)
    name = models.CharField(db_column='Name', max_length=100)
    surname = models.CharField(db_column='Surname', max_length=100)
    address = models.CharField(db_column='Address', max_length=100)
    phone_number = models.CharField(db_column='Phone_Number', max_length=45, blank=True, null=True)
    branch = models.CharField(db_column='Branch', max_length=100)
    gender = models.CharField(db_column='Gender', max_length=45)
    registration_year = models.IntegerField(db_column='Registration_Year', blank=True, null=True)
    number_of_dependants = models.IntegerField(db_column='Number_Of_Dependants')
    branch_member_number = models.CharField(db_column='Branch_Member_Number', max_length=10, unique=True)

    class Meta:
        managed = False
        db_table = 'Main_Members'
        unique_together = (('card_number', 'name', 'surname'),)


class Dependents(models.Model):
    iddependents = models.AutoField(db_column='idDependents', primary_key=True)  # Field name made lowercase.
    card_number = models.IntegerField(db_column='Card_Number')  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=100)  # Field name made lowercase.
    surname = models.CharField(db_column='Surname', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Dependents'


class Treasury(models.Model):
    idtreasury = models.AutoField(db_column='idTreasury', primary_key=True)  # Field name made lowercase.
    idmain_member = models.IntegerField(db_column='idMain_Member')  # Field name made lowercase.
    fund = models.CharField(db_column='Fund', max_length=45)  # Field name made lowercase.
    amount = models.IntegerField(db_column='Amount')  # Field name made lowercase.
    fund_date_year = models.IntegerField(db_column='Fund_Date_Year')  # Field name made lowercase.
    fund_date_month = models.CharField(db_column='Fund_Date_Month', max_length=50)  # Field name made lowercase.
    receipt_number = models.IntegerField(db_column='Receipt_Number')  # Field name made lowercase.
    payment_date = models.DateField(db_column='Payment_Date')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Treasury'
        unique_together = (('idmain_member', 'fund', 'fund_date_year', 'fund_date_month', 'receipt_number'),)


class TreasuryDep(models.Model):
    idtreasury_dep = models.AutoField(db_column='idTreasury_Dep', primary_key=True)  # Field name made lowercase.
    card_number = models.IntegerField(db_column='Card_Number')  # Field name made lowercase.
    dependent_id = models.IntegerField(db_column='Dependent_ID')  # Field name made lowercase.
    fund = models.CharField(db_column='Fund', max_length=50)  # Field name made lowercase.
    amount = models.IntegerField(db_column='Amount')  # Field name made lowercase.
    fund_date_year = models.IntegerField(db_column='Fund_Date_Year')  # Field name made lowercase.
    fund_date_month = models.IntegerField(db_column='Fund_Date_Month')  # Field name made lowercase.
    reciept_number = models.IntegerField(db_column='Reciept_Number')  # Field name made lowercase.
    payment_date = models.DateField(db_column='Payment_Date')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Treasury_Dep'
        
        


class ActivityLog(models.Model):
    ACTIONS = (
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
        ('LOGIN', 'Logged In'),
        ('PAYMENT', 'Payment Made'),
    )

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTIONS)
    timestamp = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    description = models.TextField()

    class Meta:
        ordering = ['-timestamp']
        
class MemberPictures(models.Model):
    id = models.AutoField(primary_key=True)
    branch_member_number = models.OneToOneField(MainMembers, to_field='branch_member_number', db_column='Branch_Member_Number', on_delete=models.CASCADE)
    picture_data = models.BinaryField(null=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'Member_Pictures'
        
class Picture(models.Model):
    image = models.ImageField(upload_to='pictures/')
    upload_date = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Picture uploaded on {self.upload_date}"

    class Meta:
        ordering = ['-upload_date']
        
class Treasury(models.Model):
    FUND_CHOICES = [
        ('Annual', 'Annual'),
        ('Building Fund', 'Building Fund'),
        ('Thanksgiving', 'Thanksgiving'),
        ('Maintenance', 'Maintenance'),
        ('Blessing', 'Blessing'),
        ('Registration', 'Registration'),
    
    ]

    idtreasury = models.AutoField(db_column='idTreasury', primary_key=True)
    idmain_member = models.IntegerField(db_column='idMain_Member')
    fund = models.CharField(db_column='Fund', max_length=45, choices=FUND_CHOICES)
    amount = models.IntegerField(db_column='Amount')
    fund_date_year = models.IntegerField(db_column='Fund_Date_Year')
    fund_date_month = models.CharField(db_column='Fund_Date_Month', max_length=50)
    receipt_number = models.IntegerField(db_column='Receipt_Number')
    payment_date = models.DateField(db_column='Payment_Date')

    class Meta:
        managed = False
        db_table = 'Treasury'
        unique_together = (('idmain_member', 'fund', 'fund_date_year', 'fund_date_month', 'receipt_number'),)



    def __str__(self):
        return f"{self.user} {self.action} {self.content_type}"
    



