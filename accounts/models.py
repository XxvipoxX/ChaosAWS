from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.templatetags.static import static

class CustomUser(AbstractUser):
    MEMBERSHIP_CHOICES = [
        ('free', 'Gratis'),
        ('standard', 'Estándar'),
        ('ultimate', 'Ultimate')
    ]
    
    # Información básica del usuario
    membership_type = models.CharField(
        max_length=20,
        choices=MEMBERSHIP_CHOICES,
        default='free'
    )
    
    # Información de perfil
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True
    )
    
    # NUEVO CAMPO: Para avatares del sistema
    selected_avatar = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default='avatar_default.jpg'
    )
    
    birth_date = models.DateField(null=True, blank=True)
    
    # Sistema de membresía y pagos
    membership_start = models.DateTimeField(null=True, blank=True)
    membership_expiry = models.DateTimeField(null=True, blank=True)
    is_active_member = models.BooleanField(default=False)
    
    # Información de pago
    default_payment_method = models.CharField(max_length=50, blank=True, null=True)
    card_last_four = models.CharField(max_length=4, blank=True, null=True)

    def __str__(self):
        return self.username
    
    def get_profile_picture_url(self):
        """Retorna la URL del avatar con prioridad correcta"""
        # PRIMERO: Si hay imagen subida, usarla
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        
        # SEGUNDO: Si hay avatar del sistema seleccionado
        elif self.selected_avatar:
            return static(f'assets/{self.selected_avatar}')
        
        # TERCERO: Avatar por defecto
        else:
            return static('assets/avatar_default.jpg')
    
    @property
    def get_membership_type_display(self):
        """Método para obtener el nombre legible de la membresía"""
        return dict(self.MEMBERSHIP_CHOICES).get(self.membership_type, 'Gratis')
    
    @property
    def is_membership_active(self):
        """Verificar si la membresía está activa"""
        if self.membership_expiry:
            return timezone.now() < self.membership_expiry
        return self.is_active_member
    
    def activate_membership(self, plan_type, duration_days=30):
        """Activar o renovar membresía"""
        self.membership_type = plan_type
        self.membership_start = timezone.now()
        self.membership_expiry = timezone.now() + timezone.timedelta(days=duration_days)
        self.is_active_member = True
        self.save()
    
    def get_remaining_days(self):
        """Obtener días restantes de membresía"""
        if self.membership_expiry and self.is_membership_active:
            remaining = self.membership_expiry - timezone.now()
            return max(0, remaining.days)
        return 0

class PaymentOrder(models.Model):
    PLAN_CHOICES = [
        ('free', 'Gratis'),
        ('standard', 'Estándar'),
        ('ultimate', 'Ultimate'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('cancelled', 'Cancelado'),
        ('refunded', 'Reembolsado'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Tarjeta de Crédito'),
        ('debit_card', 'Tarjeta de Débito'),
        ('paypal', 'PayPal'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True)
    card_last_four = models.CharField(max_length=4, blank=True, null=True)
    customer_email = models.EmailField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Información de suscripción
    subscription_start = models.DateTimeField(null=True, blank=True)
    subscription_end = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Orden #{self.id} - {self.user.username} - {self.get_plan_type_display()}"
    
    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.paid_at:
            self.paid_at = timezone.now()
            # Establecer fechas de suscripción
            if not self.subscription_start:
                self.subscription_start = timezone.now()
            if not self.subscription_end:
                self.subscription_end = timezone.now() + timezone.timedelta(days=30)
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        """Verificar si la suscripción está activa"""
        if self.subscription_end:
            return timezone.now() < self.subscription_end
        return self.status == 'completed'
    
    def get_plan_display_name(self):
        """Obtener nombre legible del plan"""
        return dict(self.PLAN_CHOICES).get(self.plan_type, self.plan_type)