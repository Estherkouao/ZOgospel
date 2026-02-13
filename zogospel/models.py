from django.db import models


class Magazine(models.Model):
    titre = models.CharField(max_length=200)
    categorie = models.CharField(max_length=100)
    image = models.ImageField(upload_to='magazine/')
    description = models.TextField()
    date_publication = models.DateField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='magazine/pdfs/', blank=True, null=True)

    def __str__(self):
        return self.titre


class Actualite(models.Model):
    titre = models.CharField(max_length=200)
    type_actualite = models.CharField(max_length=100)
    REGION_CHOICES = (
        ('local', 'Local'),
        ('afrique', 'Afrique'),
        ('international', 'International'),
    )
    region = models.CharField(max_length=20, choices=REGION_CHOICES, default='local')
    image = models.ImageField(upload_to='actualites/')
    contenu = models.TextField()
    date = models.DateField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.titre


class Musique(models.Model):
    titre = models.CharField(max_length=150)
    artiste = models.CharField(max_length=150)
    image = models.ImageField(upload_to='musique/')
    fichier_audio = models.FileField(upload_to='musique/audio/', blank=True, null=True)
    likes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.titre


class Agenda(models.Model):
    titre = models.CharField(max_length=200)
    lieu = models.CharField(max_length=200)
    description = models.TextField()
    TYPE_CHOICES = (
        ('concert', 'Concert'),
        ('conference', 'Conférence'),
        ('showcase', 'Showcase'),
        ('other', 'Autre'),
    )
    type_evenement = models.CharField(max_length=20, choices=TYPE_CHOICES, default='other')
    date_evenement = models.DateField()
    image = models.ImageField(upload_to='agenda/', blank=True, null=True)

    def __str__(self):
        return self.titre


class Contact(models.Model):
    nom = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom


class Inscription(models.Model):
    # inscription for an Actualite (event)
    actualite = models.ForeignKey(Actualite, on_delete=models.CASCADE, related_name='inscriptions')
    nom = models.CharField(max_length=150)
    email = models.EmailField()
    date_inscription = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} - {self.actualite.titre}"


class Ticket(models.Model):
    # Billet pour un Agenda event
    agenda = models.ForeignKey(Agenda, on_delete=models.CASCADE, related_name='tickets')
    nom = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    payment_method = models.CharField(max_length=30, choices=(('momo','Mobile Money'),('card','Carte Bancaire')), default='momo')
    paid = models.BooleanField(default=False)
    reference = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Billet #{self.id} - {self.agenda.titre} - {self.nom}"


class Rubrique(models.Model):
    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=150)
    desc = models.TextField(blank=True)
    accroche = models.CharField(max_length=200, blank=True)
    color = models.CharField(max_length=7, default='#8A2BE2')
    icon = models.CharField(max_length=8, default='🎤')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title
