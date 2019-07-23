from django.contrib import admin
from .models import Course, Question


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


class CourseAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ['course_name', 'questions_count']

    def questions_count(self, object):
        print(object)
        return object.question_set.all().count()


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['question_text']}),
        ('Date information', {'fields': [
         'pub_date'], 'classes': ['collapse']}),
    ]
    list_display = ('question_text', 'pub_date',
                    'course', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question_text']


admin.site.register(Course, CourseAdmin)
admin.site.register(Question, QuestionAdmin)
