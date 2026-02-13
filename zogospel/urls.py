

from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.accueil, name='accueil'),
    path('magazine/', views.magazine, name='magazine'),
    path('actualites/', views.actualites, name='actualites'),
    path('musique/', views.musique, name='musique'),
    path('agenda/', views.agenda, name='agenda'),
    path('contact/', views.contact, name='contact'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('add-magazine/', views.add_magazine, name='add_magazine'),
    path('add-actualite/', views.add_actualite, name='add_actualite'),
    path('add-agenda/', views.add_agenda, name='add_agenda'),
    path('add-rubrique/', views.add_rubrique, name='add_rubrique'),
    path('register-actualite/<int:id>/', views.register_actualite, name='register_actualite'),
    path('ticket/<int:inscription_id>/', views.ticket_download, name='ticket_download'),
    path('purchase/<int:agenda_id>/', views.purchase_ticket, name='purchase_ticket'),
    path('payment/<int:ticket_id>/', views.payment_instructions, name='payment_instructions'),
    path('payment/initiate/<int:ticket_id>/', views.initiate_payment, name='initiate_payment'),
    path('payment/return/', views.payment_return, name='payment_return'),
    path('payment/notify/', views.payment_notify, name='payment_notify'),
    path('ticket-agenda/<int:ticket_id>/', views.ticket_agenda_download, name='ticket_agenda_download'),
    path('register-agenda/<int:agenda_id>/', views.register_agenda, name='register_agenda'),
    path('rubriques/', views.rubriques, name='rubriques'),
    path('a-propos/', views.apropos, name='a_propos'),
    path('actualite/<int:id>/', views.actualite_detail, name='actualite_detail'),
    path('magazine/<int:id>/', views.magazine_detail, name='magazine_detail'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('add-music/', views.add_music, name='add_music'),
    path('delete-music/<int:id>/', views.delete_music, name='delete_music'),
    path('delete-rubrique/<int:id>/', views.delete_rubrique, name='delete_rubrique'),
    path('delete-magazine/<int:id>/', views.delete_magazine, name='delete_magazine'),
    path('delete-agenda/<int:id>/', views.delete_agenda, name='delete_agenda'),
    path('delete-article/<int:id>/', views.delete_actualite, name='delete_actualite'),
    path('edit-article/<int:id>/', views.edit_actualite, name='edit_actualite'),
    path('edit-magazine/<int:id>/', views.edit_magazine, name='edit_magazine'),
    path('edit-agenda/<int:id>/', views.edit_agenda, name='edit_agenda'),
    path('edit-rubrique/<int:id>/', views.edit_rubrique, name='edit_rubrique'),
    path('edit-music/<int:id>/', views.edit_music, name='edit_music'),
    path('like-actualite/<int:id>/', views.like_actualite, name='like_actualite'),
    path('like-musique/<int:id>/', views.like_musique, name='like_musique'),
    path('delete-contact/<int:id>/', views.delete_contact, name='delete_contact'),

]
