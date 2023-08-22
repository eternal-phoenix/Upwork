from django.contrib import admin

# Register your models here.


from parser_app import models


@admin.register(models.JobOfferInfo)
class JobOfferInfoAdmin(admin.ModelAdmin):
    list_display = ( 'category', 'offer_name', 'job_type', 'salary', 'offer_link', 'offer_id', 'date_posted',)


@admin.register(models.Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('link', 'status')


@admin.register(models.SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ('name', 'active')
    list_editable = ('active', )