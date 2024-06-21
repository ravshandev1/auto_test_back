from django.db import models
import os


class Theme(models.Model):
    name_uz = models.CharField(max_length=250)
    name_ru = models.CharField(max_length=250)

    def __str__(self):
        return self.name_uz


class Question(models.Model):
    theme = models.ForeignKey(Theme, models.CASCADE, 'questions')
    text_uz = models.TextField()
    text_ru = models.TextField()
    image = models.FileField(upload_to='questions/', null=True, blank=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizs'

    def __str__(self):
        return self.text_uz

    def delete(self, *args, **kwargs):
        if self.image:
            os.remove(self.image.path)
        super().delete(*args, **kwargs)

    @property
    def image_path(self):
        if self.image:
            return self.image.url
        return None


class Answer(models.Model):
    question = models.ForeignKey(Question, models.CASCADE, 'answers')
    text_uz = models.TextField()
    text_ru = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text_uz


class TelegramUser(models.Model):
    name = models.CharField(max_length=250)
    phone_number = models.CharField(max_length=250)
    telegram_id = models.BigIntegerField(unique=True)
    lang = models.CharField(max_length=2)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Quiz(models.Model):
    user = models.ForeignKey(TelegramUser, models.CASCADE, 'quizzes')
    theme = models.ForeignKey(Theme, models.CASCADE, 'quizzes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name

    class Meta:
        verbose_name = "Test"
        verbose_name_plural = "Tests"

    @property
    def result_count(self):
        qs = self.answers.all()
        cntr = 0
        for i in qs:
            if i.answer.is_correct:
                cntr += 1
        return f"{cntr}/{qs.count()}"

    @property
    def result_percentage(self):
        qs = self.answers.all()
        count = qs.count()
        cntr = 0
        for i in qs:
            if i.answer.is_correct:
                cntr += 1
        if qs.count() == 0:
            count = 1
        percentage = round((cntr * 100) / count)
        return f"{percentage}%"


class QuizAnswer(models.Model):
    quiz = models.ForeignKey(Quiz, models.CASCADE, 'answers')
    question = models.ForeignKey(Question, models.CASCADE, 'quiz_answers')
    answer = models.ForeignKey(Answer, models.CASCADE, 'quiz_answers')
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.answer.text_uz


class Rate(models.Model):
    name_uz = models.CharField(max_length=250, unique=True)
    name_ru = models.CharField(max_length=250, unique=True)
    days = models.IntegerField()
    price = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name_uz

    class Meta:
        verbose_name = "Tariff"
        verbose_name_plural = "Tariffs"


class PaymentType(models.Model):
    name = models.CharField(max_length=250, unique=True)
    is_active = models.BooleanField(default=True)
    token = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Provider"
        verbose_name_plural = "Providers"


class Payment(models.Model):
    user = models.ForeignKey(TelegramUser, models.CASCADE, 'payments')
    provider = models.ForeignKey(PaymentType, models.CASCADE, 'payments')
    rate = models.ForeignKey(Rate, models.CASCADE, 'payments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name


class Subscription(models.Model):
    user = models.ForeignKey(TelegramUser, models.CASCADE, 'subscriptions')
    rate = models.ForeignKey(Rate, models.CASCADE, 'subscriptions')
    end_at = models.DateField()

    def __str__(self):
        return f"{self.user} {self.end_at}"


class About(models.Model):
    text_uz = models.TextField()
    text_ru = models.TextField()

    def __str__(self):
        return self.text_uz

    class Meta:
        verbose_name = "Бот ҳақида"
        verbose_name_plural = "Бот ҳақида"


class Information(models.Model):
    class Meta:
        verbose_name = 'Маълумотлар'
        verbose_name_plural = 'Маълумотлар'

    image = models.FileField(upload_to='images')
    text_uz = models.TextField()
    text_ru = models.TextField()

    def __str__(self):
        return self.image.name
