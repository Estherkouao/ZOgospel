from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from .models import Magazine, Actualite, Musique, Agenda, Contact, Rubrique, Inscription, Ticket
from django.utils.crypto import get_random_string

import json
import io
try:
    from xhtml2pdf import pisa
except Exception:
    pisa = None

# CONFIGURATION CINETPAY (À REMPLACER PAR VOS CLÉS RÉELLES)
CINETPAY_API_KEY = "VOTRE_API_KEY_ICI" 
CINETPAY_SITE_ID = "VOTRE_SITE_ID_ICI"
CINETPAY_BASE_URL = "https://api-checkout.cinetpay.com/v2/payment"

def admin_login(request):
    if request.method == 'POST':
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            return render(request, 'admin/login.html', {'error': True})
    return render(request, 'admin/login.html')


@login_required
def add_music(request):
    if request.method == 'POST':
        Musique.objects.create(
            titre=request.POST['title'],
            artiste=request.POST['artist'],
            image=request.FILES.get('image'),
            fichier_audio=request.FILES.get('audio_file')
        )
        return redirect('admin_dashboard')
    return render(request, 'admin/add_music.html')

@login_required
def delete_music(request, id):
    Musique.objects.filter(id=id).delete()
    return redirect('admin_dashboard')


@login_required
def add_magazine(request):
    if request.method == 'POST':
        magazine = Magazine(
            titre=request.POST.get('titre'),
            categorie=request.POST.get('categorie'),
            image=request.FILES.get('image'),
            description=request.POST.get('description'),
        )
        if request.FILES.get('pdf_file'):
            magazine.pdf_file = request.FILES.get('pdf_file')
        magazine.save()
        return redirect('admin_dashboard')
    return render(request, 'admin/add_magazine.html')


@login_required
def edit_magazine(request, id):
    magazine = get_object_or_404(Magazine, id=id)
    if request.method == 'POST':
        magazine.titre = request.POST.get('titre')
        magazine.categorie = request.POST.get('categorie')
        magazine.description = request.POST.get('description')
        new_image = request.FILES.get('image')
        if new_image:
            try:
                if magazine.image and hasattr(magazine.image, 'delete'):
                    magazine.image.delete(save=False)
            except Exception:
                pass
            magazine.image = new_image
        new_pdf = request.FILES.get('pdf_file')
        if new_pdf:
            try:
                if magazine.pdf_file and hasattr(magazine.pdf_file, 'delete'):
                    magazine.pdf_file.delete(save=False)
            except Exception:
                pass
            magazine.pdf_file = new_pdf
        magazine.save()
        return redirect('admin_dashboard')
    return render(request, 'admin/add_magazine.html', {'magazine': magazine, 'edit': True})


@login_required
def add_actualite(request):
    if request.method == 'POST':
        Actualite.objects.create(
            titre=request.POST.get('titre'),
            type_actualite=request.POST.get('type_actualite'),
            image=request.FILES.get('image'),
            contenu=request.POST.get('contenu'),
        )
        return redirect('admin_dashboard')
    return render(request, 'admin/add_actualite.html')


@login_required
def edit_actualite(request, id):
    actualite = get_object_or_404(Actualite, id=id)
    if request.method == 'POST':
        actualite.titre = request.POST.get('titre')
        actualite.type_actualite = request.POST.get('type_actualite')
        actualite.contenu = request.POST.get('contenu')
        # replace image if new one uploaded
        new_image = request.FILES.get('image')
        if new_image:
            try:
                if actualite.image and hasattr(actualite.image, 'delete'):
                    actualite.image.delete(save=False)
            except Exception:
                pass
            actualite.image = new_image
        actualite.save()
        return redirect('admin_dashboard')
    return render(request, 'admin/add_actualite.html', {'actualite': actualite, 'edit': True})


@login_required
def delete_actualite(request, id):
    actualite = get_object_or_404(Actualite, id=id)
    try:
        if actualite.image and hasattr(actualite.image, 'delete'):
            actualite.image.delete(save=False)
    except Exception:
        pass
    actualite.delete()
    return redirect('admin_dashboard')


@login_required
def add_agenda(request):
    if request.method == 'POST':
        date_str = request.POST.get('date_evenement')
        try:
            date_evenement = datetime.strptime(date_str, '%Y-%m-%d').date()
        except Exception:
            date_evenement = datetime.today().date()
        Agenda.objects.create(
            titre=request.POST.get('titre'),
            lieu=request.POST.get('lieu'),
            description=request.POST.get('description'),
            type_evenement=request.POST.get('type_evenement', 'other'),
            image=request.FILES.get('image'),
            date_evenement=date_evenement,
        )
        return redirect('admin_dashboard')
    return render(request, 'admin/add_agenda.html')


@login_required
def edit_agenda(request, id):
    agenda_obj = get_object_or_404(Agenda, id=id)
    if request.method == 'POST':
        agenda_obj.titre = request.POST.get('titre')
        agenda_obj.lieu = request.POST.get('lieu')
        agenda_obj.description = request.POST.get('description')
        date_str = request.POST.get('date_evenement')
        try:
            agenda_obj.date_evenement = datetime.strptime(date_str, '%Y-%m-%d').date()
        except Exception:
            pass
        agenda_obj.type_evenement = request.POST.get('type_evenement', agenda_obj.type_evenement)
        new_image = request.FILES.get('image')
        if new_image:
            try:
                if agenda_obj.image and hasattr(agenda_obj.image, 'delete'):
                    agenda_obj.image.delete(save=False)
            except Exception:
                pass
            agenda_obj.image = new_image
        agenda_obj.save()
        return redirect('admin_dashboard')
    return render(request, 'admin/add_agenda.html', {'agenda': agenda_obj, 'edit': True})


def register_actualite(request, id):
        # allow user to register for an actualite (event)
        actualite = get_object_or_404(Actualite, id=id)
        if request.method == 'POST':
                nom = request.POST.get('nom')
                email = request.POST.get('email')
                inscription = Inscription.objects.create(actualite=actualite, nom=nom, email=email)
                return redirect('ticket_download', inscription_id=inscription.id)
        # if GET, render a small registration page
        return render(request, 'register_actualite.html', {'actualite': actualite})


def ticket_download(request, inscription_id):
        inscription = get_object_or_404(Inscription, id=inscription_id)
        # create a nicer HTML ticket for download following the artistic direction
        content = f"""
        <!doctype html>
        <html lang="fr">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width,initial-scale=1">
            <title>Ticket-{inscription.id}</title>
            <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&family=Roboto:wght@300;400&family=Playfair+Display:ital,wght@0,400;1,400&display=swap" rel="stylesheet">
            <style>
                :root{{--gold:#D4AF37;--violet:#8A2BE2;--black:#1A1A1A;--white:#ffffff}}
                body{{font-family: Roboto, Arial, sans-serif; background:#f6f5f3; padding:30px; color:var(--black)}}
                .ticket{{max-width:820px;margin:0 auto;background:var(--white);border-radius:14px;overflow:hidden;border:4px solid rgba(212,175,55,0.15);box-shadow:0 10px 30px rgba(0,0,0,0.08)}}
                .ticket-header{{background:linear-gradient(90deg, rgba(26,26,26,0.95), rgba(26,26,26,0.95));color:var(--gold);padding:28px 36px;display:flex;align-items:center;justify-content:space-between}}
                .brand{{font-family:Montserrat, sans-serif;font-weight:700;letter-spacing:0.06em;font-size:22px}}
                .sub{{font-size:11px;color:#fff;opacity:0.85;margin-left:12px}}
                .ticket-body{{display:flex;gap:30px;padding:30px 36px}}
                .details{{flex:1}}
                .details h1{{font-family:Playfair Display, serif;font-size:28px;margin:0;color:var(--black)}}
                .meta{{margin-top:12px;color:#555;font-size:15px}}
                .field{{margin-top:18px}}
                .label{{font-size:12px;color:#777;letter-spacing:0.06em;text-transform:uppercase}}
                .value{{font-size:16px;color:var(--black);font-weight:600;margin-top:6px}}
                .cta{{margin-top:22px;display:inline-block;background:var(--violet);color:var(--white);padding:10px 16px;border-radius:8px;text-decoration:none;font-weight:600}}
                .aside{{width:260px;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:10px 20px;border-left:1px dashed rgba(0,0,0,0.06)}}
                .qr{{width:170px;height:170px;background:linear-gradient(135deg,#eee,#fff);display:flex;align-items:center;justify-content:center;border-radius:8px;border:2px solid rgba(0,0,0,0.04)}}
                .ref{{margin-top:12px;font-weight:700;color:var(--gold)}}
                .footer{{background:#faf8f6;padding:18px 36px;font-size:13px;color:#666;display:flex;justify-content:space-between;align-items:center}}
                @media (max-width:800px){{.ticket-body{{flex-direction:column}}.aside{{width:100%;border-left:none;border-top:1px dashed rgba(0,0,0,0.06);padding-top:18px}}}}
            </style>
        </head>
        <body>
            <div class="ticket">
                <div class="ticket-header">
                    <div style="display:flex;align-items:center">
                        <div class="brand">EXCELLENCE</div>
                        <div class="sub">ZO Gospel — Ticket officiel</div>
                    </div>
                    <div style="text-align:right">
                        <div style="font-size:12px;color:#fff;opacity:0.9">Référence</div>
                        <div style="font-weight:700;color:var(--gold);font-size:16px">#{inscription.id}</div>
                    </div>
                </div>

                <div class="ticket-body">
                    <div class="details">
                        <h1>{inscription.actualite.titre}</h1>
                        <div class="meta">{inscription.actualite.type_actualite} • {inscription.actualite.date.strftime('%d %B %Y')}</div>

                        <div class="field">
                            <div class="label">Participant</div>
                            <div class="value">{inscription.nom}</div>
                        </div>

                        <div class="field">
                            <div class="label">Email</div>
                            <div class="value">{inscription.email}</div>
                        </div>

                        <a class="cta" href="#">Conservez ce ticket — Présentez-le à l'entrée</a>
                    </div>

                    <div class="aside">
                        <div class="qr">
                            <!-- simple SVG barcode-style placeholder with id -->
                            <svg width="140" height="140" xmlns="http://www.w3.org/2000/svg">
                                <rect width="140" height="140" fill="#fff" rx="8"/>
                                <g fill="#111">
                                    <rect x="8" y="8" width="10" height="40"/>
                                    <rect x="26" y="8" width="6" height="60"/>
                                    <rect x="38" y="8" width="10" height="30"/>
                                    <rect x="56" y="8" width="6" height="80"/>
                                    <rect x="70" y="8" width="10" height="50"/>
                                    <rect x="90" y="8" width="6" height="70"/>
                                </g>
                                <text x="70" y="128" font-size="12" text-anchor="middle" fill="#8A2BE2">ID {inscription.id}</text>
                            </svg>
                        </div>
                        <div class="ref">Réf. #{inscription.id}</div>
                        <div style="margin-top:8px;font-size:12px;color:#666;text-align:center">Valable uniquement pour l'événement indiqué. Veuillez présenter ce ticket imprimé ou sur mobile.</div>
                    </div>
                </div>

                <div class="footer">
                    <div>Produit par EXCELLENCE • ZO Gospel</div>
                    <div style="color:var(--gold);font-weight:700">Merci et à bientôt</div>
                </div>
            </div>
        </body>
        </html>
        """
        response = HttpResponse(content, content_type='text/html; charset=utf-8')
        filename = f"ticket-{inscription.id}.html"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


def purchase_ticket(request, agenda_id):
    agenda_obj = get_object_or_404(Agenda, id=agenda_id)
    if request.method == 'POST':
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        payment_method = request.POST.get('payment_method')
        ref = get_random_string(10).upper()
        ticket = Ticket.objects.create(agenda=agenda_obj, nom=nom, email=email, phone=phone, payment_method=payment_method, reference=ref)
        # Redirection directe vers l'initialisation du paiement réel
        return redirect('initiate_payment', ticket_id=ticket.id)
    return render(request, 'purchase_ticket.html', {'agenda': agenda_obj})


def payment_instructions(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    return render(request, 'payment_instructions.html', {'ticket': ticket})


def initiate_payment(request, ticket_id):
    """Initialise le paiement avec l'API CinetPay"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Construction de l'URL de retour absolue
    return_url = request.build_absolute_uri(reverse('payment_return'))
    notify_url = request.build_absolute_uri(reverse('payment_notify'))
    
    payload = {
        "apikey": CINETPAY_API_KEY,
        "site_id": CINETPAY_SITE_ID,
        "transaction_id": ticket.reference,
        "amount": 5000,  # Montant (à dynamiser selon l'agenda si besoin)
        "currency": "XOF",
        "description": f"Ticket - {ticket.agenda.titre}",
        "customer_name": ticket.nom,
        "customer_email": ticket.email,
        "customer_phone_number": ticket.phone,
        "channels": "ALL",
        "return_url": return_url,
        "notify_url": notify_url,
    }
    
    try:
        response = requests.post(CINETPAY_BASE_URL, json=payload)
        result = response.json()
        
        if result.get('code') == '201':
            # Redirection vers le guichet de paiement CinetPay
            return redirect(result['data']['payment_url'])
        else:
            messages.error(request, f"Erreur API: {result.get('description')}")
    except Exception as e:
        messages.error(request, "Erreur de connexion au service de paiement.")
        
    # En cas d'erreur, on retourne aux instructions manuelles
    return redirect('payment_instructions', ticket_id=ticket.id)

@csrf_exempt
def payment_notify(request):
    """Webhook appelé par CinetPay pour confirmer le paiement (Server-to-Server)"""
    if request.method == 'POST':
        data = request.POST
        cpm_trans_id = data.get('cpm_trans_id')
        # Ici, il faudrait idéalement vérifier le statut auprès de CinetPay via leur API de vérification
        # Pour l'instant, on marque comme payé si on reçoit la notif
        try:
            ticket = Ticket.objects.get(reference=cpm_trans_id)
            ticket.paid = True
            ticket.save()
        except Ticket.DoesNotExist:
            pass
    return HttpResponse("OK")

def payment_return(request):
    """Page de retour après paiement"""
    transaction_id = request.POST.get('transaction_id') or request.GET.get('transaction_id')
    
    if transaction_id:
        # Vérification du statut via API CinetPay (recommandé)
        check_url = "https://api-checkout.cinetpay.com/v2/payment/check"
        payload = {
            "apikey": CINETPAY_API_KEY,
            "site_id": CINETPAY_SITE_ID,
            "transaction_id": transaction_id
        }
        try:
            response = requests.post(check_url, json=payload)
            result = response.json()
            if result.get('code') == '00': # Code 00 = Succès
                ticket = get_object_or_404(Ticket, reference=transaction_id)
                ticket.paid = True
                ticket.save()
                return redirect('payment_instructions', ticket_id=ticket.id)
        except Exception:
            pass
            
    messages.error(request, "Le paiement n'a pas pu être validé.")
    return redirect('accueil')

def ticket_agenda_download(request, ticket_id):
        ticket = get_object_or_404(Ticket, id=ticket_id)

        # build a nicer HTML for the ticket
        html = f'''
<!doctype html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Billet-{ticket.id}</title>
    <style>
        @page {{ size: A4; margin: 24mm 18mm 24mm 18mm; }}
        body {{ font-family: Helvetica, Arial, sans-serif; color: #111; }}
        .ticket {{ max-width: 760px; margin: 0 auto; border-radius: 12px; overflow: hidden; border: 6px solid #D4AF37; }}
        .header {{ background: #111; color: white; padding: 18px 22px; display:flex; justify-content:space-between; align-items:center }}
        .brand {{ font-weight:700; letter-spacing:0.06em; font-size:20px; }}
        .body {{ display:flex; padding:22px; gap:18px }}
        .left {{ flex:1 }}
        .title {{ font-family: 'Times', serif; font-size:22px; margin:0 0 6px 0 }}
        .meta {{ color:#555; font-size:13px; margin-bottom:12px }}
        .field-label {{ font-size:10px; color:#777; text-transform:uppercase; letter-spacing:0.06em }}
        .field-value {{ font-size:14px; font-weight:600; margin-top:6px }}
        .aside {{ width:220px; text-align:center; border-left:1px solid #eee; padding-left:16px }}
        .qrbox {{ width:160px; height:160px; margin:0 auto 8px auto; border-radius:8px; background:#fff; border:2px solid #eee; display:flex; align-items:center; justify-content:center }}
        .footer {{ background:#faf8f6; padding:12px 18px; font-size:12px; display:flex; justify-content:space-between; align-items:center }}
    </style>
</head>
<body>
    <div class="ticket">
        <div class="header">
            <div><div class="brand">EXCELLENCE</div><div style="font-size:11px; opacity:0.9">ZO Gospel — Billet Officiel</div></div>
            <div style="text-align:right"><div style="font-size:11px; opacity:0.9">Réf.</div><div style="font-weight:700; color:#D4AF37">#{ticket.reference or ticket.id}</div></div>
        </div>
        <div class="body">
            <div class="left">
                <h1 class="title">{ticket.agenda.titre}</h1>
                <div class="meta">{ticket.agenda.type_evenement.title()} • {ticket.agenda.date_evenement.strftime('%d %B %Y')}</div>

                <div style="margin-top:12px">
                    <div class="field-label">Participant</div>
                    <div class="field-value">{ticket.nom}</div>
                </div>
                <div style="margin-top:10px">
                    <div class="field-label">Email</div>
                    <div class="field-value">{ticket.email}</div>
                </div>
                <div style="margin-top:10px">
                    <div class="field-label">Téléphone</div>
                    <div class="field-value">{ticket.phone or '—'}</div>
                </div>
                <div style="margin-top:16px"><strong>Statut :</strong> {'Payé' if ticket.paid else 'En attente'}</div>
            </div>
            <div class="aside">
                <div class="qrbox">
                    <svg width="120" height="120" xmlns="http://www.w3.org/2000/svg">
                        <rect width="120" height="120" fill="#fff" rx="6"/>
                        <g fill="#111">
                            <rect x="8" y="8" width="10" height="36"/>
                            <rect x="28" y="8" width="6" height="56"/>
                            <rect x="40" y="8" width="10" height="26"/>
                            <rect x="60" y="8" width="6" height="72"/>
                            <rect x="74" y="8" width="10" height="46"/>
                            <rect x="94" y="8" width="6" height="62"/>
                        </g>
                    </svg>
                </div>
                <div style="margin-top:6px; font-weight:700; color:#D4AF37">Réf. {ticket.reference or ticket.id}</div>
                <div style="margin-top:8px; font-size:11px; color:#666">Présentez ce billet imprimé ou sur mobile à l'entrée.</div>
            </div>
        </div>
        <div class="footer">
            <div>Produit par EXCELLENCE • ZO Gospel</div>
            <div style="color:#D4AF37; font-weight:700">Merci et à bientôt</div>
        </div>
    </div>
</body>
</html>
'''

        # If xhtml2pdf available, render PDF
        if pisa:
                result = io.BytesIO()
                pisa_status = pisa.CreatePDF(io.BytesIO(html.encode('utf-8')), dest=result)
                if pisa_status.err:
                        # on error, return HTML as fallback
                        resp = HttpResponse(html, content_type='text/html; charset=utf-8')
                        resp['Content-Disposition'] = f'attachment; filename="billet-{ticket.id}.html"'
                        return resp
                pdf = result.getvalue()
                resp = HttpResponse(pdf, content_type='application/pdf')
                resp['Content-Disposition'] = f'attachment; filename="billet-{ticket.id}.pdf"'
                return resp
        else:
                # fallback: return HTML (user can save as PDF locally)
                resp = HttpResponse(html, content_type='text/html; charset=utf-8')
                resp['Content-Disposition'] = f'attachment; filename="billet-{ticket.id}.html"'
                return resp


def register_agenda(request, agenda_id):
    agenda_obj = get_object_or_404(Agenda, id=agenda_id)
    if request.method == 'POST':
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        ref = get_random_string(8).upper()
        # create ticket marked as paid (free registration) and return download
        ticket = Ticket.objects.create(agenda=agenda_obj, nom=nom, email=email, phone=phone, payment_method='free', paid=True, reference=ref)
        return redirect('ticket_agenda_download', ticket_id=ticket.id)
    return render(request, 'register_agenda.html', {'agenda': agenda_obj})


@login_required
def admin_dashboard(request):
    context = {
        'musique_count': Musique.objects.count(),
        'article_count': Actualite.objects.count(),
        'contact_count': Contact.objects.count(),
        'musiques': Musique.objects.all(),
        'articles': Actualite.objects.all(),
        'rubriques': Rubrique.objects.all(),
        'magazines': Magazine.objects.all(),
        'agendas': Agenda.objects.all(),
        'contacts': Contact.objects.all().order_by('-id'),
    }
    return render(request, 'admin/dashboard.html', context)


@login_required
def delete_rubrique(request, id):
    rubrique = get_object_or_404(Rubrique, id=id)
    rubrique.delete()
    return redirect('admin_dashboard')


@login_required
def delete_magazine(request, id):
    magazine = get_object_or_404(Magazine, id=id)
    # delete image file if present
    try:
        if magazine.image and hasattr(magazine.image, 'delete'):
            magazine.image.delete(save=False)
    except Exception:
        pass
    magazine.delete()
    return redirect('admin_dashboard')


@login_required
def delete_agenda(request, id):
    agenda_obj = get_object_or_404(Agenda, id=id)
    try:
        if agenda_obj.image and hasattr(agenda_obj.image, 'delete'):
            agenda_obj.image.delete(save=False)
    except Exception:
        pass
    agenda_obj.delete()
    return redirect('admin_dashboard')

@login_required
def delete_contact(request, id):
    contact = get_object_or_404(Contact, id=id)
    contact.delete()
    return redirect('admin_dashboard')

@login_required
def admin_logout(request):
    logout(request)
    return redirect('admin_login')





def home(request):
    return render(request, 'zogospel.html')




def accueil(request):
    magazines = Magazine.objects.all().order_by('-date_publication')[:3]
    musiques = Musique.objects.all()[:4]
    actualites = Actualite.objects.all()[:2]

    context = {
        'magazines': magazines,
        'musiques': musiques,
        'actualites': actualites
    }
    return render(request, 'accueil.html', context)


def magazine(request):
    magazines = Magazine.objects.all()
    return render(request, 'magazine.html', {'magazines': magazines})


def actualites(request):
    selected_region = request.GET.get('region')
    actualites = Actualite.objects.all().order_by('-date')
    if selected_region in ('local', 'afrique', 'international'):
        actualites = actualites.filter(region=selected_region)
    return render(request, 'actualites.html', {'actualites': actualites, 'selected_region': selected_region})


def musique(request):
    musiques = Musique.objects.all()
    return render(request, 'musique.html', {'musiques': musiques})


def agenda(request):
    selected_type = request.GET.get('type')
    evenements = Agenda.objects.all().order_by('date_evenement')
    if selected_type in ('concert', 'conference', 'showcase'):
        evenements = evenements.filter(type_evenement=selected_type)
    return render(request, 'agenda.html', {'evenements': evenements, 'selected_type': selected_type})


def apropos(request):
    """Page À propos: sections statiques."""
    return render(request, 'a_propos.html')


def contact(request):
    if request.method == 'POST':
        Contact.objects.create(
            nom=request.POST.get('nom'),
            email=request.POST.get('email'),
            message=request.POST.get('message')
        )
        messages.success(request, "Votre message a été envoyé avec succès !")
        return redirect('contact')

    return render(request, 'contact.html')


def get_default_rubriques():
    return [
        {
            'slug': 'interview',
            'titre': 'INTERVIEW',
            'desc': 'Un espace d’échange authentique avec les acteurs du gospel : artistes, leaders chrétiens, producteurs, communicateurs et influenceurs. Les interviews de ZO GOSPEL vont au-delà de la musique pour explorer la foi, la vision, les combats et l’impact spirituel de chaque invité.',
            'color': '#D4AF37',
            'icon': '🎙️',
            'items': []
        },
        {
            'slug': 'portrait',
            'titre': 'PORTRAIT',
            'desc': 'Cette rubrique met en lumière un parcours inspirant. À travers un récit humain et profond, ZO GOSPEL dresse le portrait d’hommes et de femmes qui marquent le gospel par leur engagement, leur talent et leur témoignage de vie.',
            'color': '#8A2BE2',
            'icon': '👤',
            'items': []
        },
        {
            'slug': 'gospel-news',
            'titre': 'GOSPEL NEWS / ACTUALITÉ',
            'desc': 'Toute l’actualité du gospel locale, africaine et internationale. Sorties musicales, événements, distinctions, collaborations, annonces importantes… ZO GOSPEL informe, décrypte et connecte la communauté gospel au mouvement mondial.',
            'color': '#1A1A1A',
            'icon': '📰',
            'items': []
        },
        {
            'slug': 'dossier-special',
            'titre': 'DOSSIER SPÉCIAL',
            'desc': 'Un contenu de fond qui développe une thématique forte en lien avec la foi chrétienne, la culture urbaine et la société contemporaine. Chaque dossier apporte une analyse biblique, sociale et spirituelle, avec un regard chrétien éclairé sur les réalités actuelles.',
            'color': '#D4AF37',
            'icon': '📁',
            'items': []
        },
        {
            'slug': 'temoignages',
            'titre': 'TÉMOIGNAGES',
            'desc': 'Des histoires vraies de transformation, de guérison, de restauration et de victoire par la puissance de Dieu. Cette rubrique rappelle que Christ agit encore aujourd’hui, au cœur des vies et des nations.',
            'color': '#8A2BE2',
            'icon': '🙏',
            'items': []
        },
        {
            'slug': 'agenda-gospel',
            'titre': 'AGENDA GOSPEL',
            'desc': 'Le calendrier des concerts, showcases, conférences, festivals et événements chrétiens. ZO GOSPEL permet à son public de ne rien manquer des rendez-vous gospel majeurs, en présentiel comme en ligne.',
            'color': '#1A1A1A',
            'icon': '📅',
            'items': []
        },
        {
            'slug': 'godspell',
            'titre': 'GODSPELL (PRÉDICATION)',
            'desc': 'Une rubrique spirituelle dédiée à la Parole de Dieu. Enseignements, exhortations, méditations bibliques et prédications courtes pour nourrir la foi, encourager et édifier les lecteurs.',
            'color': '#D4AF37',
            'icon': '📖',
            'items': []
        },
        {
            'slug': 'decouverte-talent',
            'titre': 'DÉCOUVERTE TALENT',
            'desc': 'ZO GOSPEL s’engage à révéler la nouvelle génération du gospel. Cette rubrique met en avant des artistes émergents, talents cachés et projets prometteurs, en leur offrant une plateforme de visibilité et d’expression.',
            'color': '#8A2BE2',
            'icon': '🌟',
            'items': []
        }
    ]


def rubriques(request):
    # Prefer database-driven rubriques; fall back to static list if none exist
    db_sections = Rubrique.objects.all()
    sections = []
    if db_sections.exists():
        for r in db_sections:
            s = {
                'slug': r.slug,
                'titre': r.title,
                'desc': r.desc,
                'color': r.color,
                'icon': r.icon,
                'accroche': r.accroche,
            }
            # fetch related items: actualites or magazines that match slug or category
            actualites = Actualite.objects.filter(type_actualite__icontains=r.slug).order_by('-date')[:4]
            magazines = Magazine.objects.filter(categorie__icontains=r.slug).order_by('-date_publication')[:4]
            items = []
            for a in actualites:
                items.append({'obj': a, 'kind': 'actualite'})
            if not items:
                for a in Actualite.objects.all().order_by('-date')[:4]:
                    items.append({'obj': a, 'kind': 'actualite'})
            if magazines.exists():
                for m in magazines:
                    items.append({'obj': m, 'kind': 'magazine'})
            s['items'] = items
            sections.append(s)
    else:
        # Fallback to the requested static list if DB is empty
        sections = get_default_rubriques()
        
        for s in sections:
            items = []
            if s['slug'] == 'agenda-gospel':
                agendas = Agenda.objects.all().order_by('date_evenement')[:4]
                for ag in agendas:
                    items.append({'obj': ag, 'kind': 'agenda'})
            else:
                actualites = Actualite.objects.filter(type_actualite__icontains=s['slug']).order_by('-date')[:4]
                for a in actualites:
                    items.append({'obj': a, 'kind': 'actualite'})
            s['items'] = items

    # supply a small "featured" list used by the template sidebar
    featured = Actualite.objects.all().order_by('-date')[:4]

    return render(request, 'rubriques.html', {'sections': sections, 'featured': featured})


def rubrique_detail(request, slug):
    # Try to find in DB first
    rubrique = Rubrique.objects.filter(slug=slug).first()
    if rubrique:
        title = rubrique.title
        desc = rubrique.desc
        color = rubrique.color
    else:
        # Fallback to static list
        defaults = get_default_rubriques()
        found = next((s for s in defaults if s['slug'] == slug), None)
        if not found:
            # If not found anywhere, redirect to rubriques list or 404
            return redirect('rubriques')
        title = found['titre']
        desc = found['desc']
        color = found['color']

    items = []
    if slug == 'agenda-gospel':
        agendas = Agenda.objects.all().order_by('date_evenement')
        for ag in agendas:
            items.append({'obj': ag, 'kind': 'agenda'})
    else:
        actualites = Actualite.objects.filter(type_actualite__icontains=slug).order_by('-date')
        for a in actualites:
            items.append({'obj': a, 'kind': 'actualite'})
        magazines = Magazine.objects.filter(categorie__icontains=slug).order_by('-date_publication')
        for m in magazines:
            items.append({'obj': m, 'kind': 'magazine'})
    
    # Sort mixed items by date (descending)
    items.sort(key=lambda x: x['obj'].date if hasattr(x['obj'], 'date') else (x['obj'].date_publication if hasattr(x['obj'], 'date_publication') else (x['obj'].date_evenement if hasattr(x['obj'], 'date_evenement') else datetime.min.date())), reverse=True)

    return render(request, 'rubrique_detail.html', {'title': title, 'desc': desc, 'color': color, 'items': items})


@login_required
def add_rubrique(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        title = request.POST.get('title')
        desc = request.POST.get('desc', '')
        accroche = request.POST.get('accroche', '')
        color = request.POST.get('color', '#8A2BE2')
        icon = request.POST.get('icon', '🎤')
        Rubrique.objects.create(slug=slug, title=title, desc=desc, accroche=accroche, color=color, icon=icon)
        return redirect('admin_dashboard')
    return render(request, 'admin/add_rubrique.html')


@login_required
def edit_rubrique(request, id):
    rubrique = get_object_or_404(Rubrique, id=id)
    if request.method == 'POST':
        rubrique.slug = request.POST.get('slug')
        rubrique.title = request.POST.get('title')
        rubrique.accroche = request.POST.get('accroche', '')
        rubrique.desc = request.POST.get('desc', '')
        rubrique.color = request.POST.get('color', rubrique.color)
        rubrique.icon = request.POST.get('icon', rubrique.icon)
        rubrique.save()
        return redirect('admin_dashboard')
    return render(request, 'admin/add_rubrique.html', {'rubrique': rubrique, 'edit': True})


@login_required
def edit_music(request, id):
    musique = get_object_or_404(Musique, id=id)
    if request.method == 'POST':
        musique.titre = request.POST.get('title')
        musique.artiste = request.POST.get('artist')
        new_image = request.FILES.get('image')
        new_audio = request.FILES.get('audio_file')
        if new_image:
            try:
                if musique.image and hasattr(musique.image, 'delete'):
                    musique.image.delete(save=False)
            except Exception:
                pass
            musique.image = new_image
        if new_audio:
            try:
                if musique.fichier_audio and hasattr(musique.fichier_audio, 'delete'):
                    musique.fichier_audio.delete(save=False)
            except Exception:
                pass
            musique.fichier_audio = new_audio
        musique.save()
        return redirect('admin_dashboard')
    return render(request, 'admin/add_music.html', {'musique': musique, 'edit': True})


def actualite_detail(request, id):
    actualite = get_object_or_404(Actualite, id=id)
    latest_actualites = Actualite.objects.exclude(id=id).order_by('-date')[:4]
    context = {
        'actualite': actualite,
        'latest_actualites': latest_actualites,
    }
    return render(request, 'actualite_detail.html', context)


def magazine_detail(request, id):
    magazine_obj = get_object_or_404(Magazine, id=id)
    return render(request, 'magazine_detail.html', {'magazine': magazine_obj})


def like_actualite(request, id):
    if request.method == 'POST':
        actualite = Actualite.objects.get(id=id)
        actualite.likes += 1
        actualite.save()
        # If AJAX request, return JSON with updated likes
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'likes': actualite.likes})
    return redirect('actualites')


def like_musique(request, id):
    if request.method == 'POST':
        musique = Musique.objects.get(id=id)
        musique.likes += 1
        musique.save()
    return redirect('musique')
