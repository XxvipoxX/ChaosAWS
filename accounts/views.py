from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .forms import LoginForm, SignupForm, CustomUserChangeForm
from .models import CustomUser, PaymentOrder
import secrets
import string
import uuid
from datetime import timedelta
import logging

# Configuración de logger
logger = logging.getLogger(__name__)

# =========================================================================
# UTILITIES
# =========================================================================

def generate_secure_token(length=32):
    """Genera un token alfanumérico seguro para restablecimiento de contraseña."""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for i in range(length))

# Test para verificar si el usuario es un miembro activo (si aplica)
def is_active_member(user):
    # Asume que CustomUser tiene un método/propiedad is_membership_active
    return user.is_active_member

# =========================================================================
# VISTAS DE AUTENTICACIÓN Y PERFIL
# =========================================================================

def login_view(request):
    logger.info("🔐 Vista login llamada")
    
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        logger.info("📨 POST recibido en login")
        form = LoginForm(request, data=request.POST)
        logger.debug(f"✅ Form login válido: {form.is_valid()}")
        
        if form.is_valid():
            logger.info("🎯 Login válido - autenticando...")
            username_or_email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me', False)
            
            # Intentar autenticar con username
            user = authenticate(request, username=username_or_email, password=password)
            
            # Si falla, intentar con email
            if user is None:
                try:
                    user_obj = CustomUser.objects.get(email__iexact=username_or_email)
                    user = authenticate(request, username=user_obj.username, password=password)
                except CustomUser.DoesNotExist:
                    user = None
                
            if user is not None:
                login(request, user)
                
                # Configurar la expiración de la sesión
                if not remember_me:
                    request.session.set_expiry(0) # Sesión expira cuando el navegador se cierra
                else:
                    request.session.set_expiry(1209600) # Sesión dura dos semanas (14 días)
                
                messages.success(request, f'¡Bienvenido de nuevo, {user.username}!')
                logger.info("🚀 Login exitoso. Redirigiendo a índice.")
                next_url = request.GET.get('next', 'index')
                return redirect(next_url) 
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
                logger.warning("❌ Autenticación fallida.")
        
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
            
    else:
        form = LoginForm()
        logger.debug("📥 Petición GET - Formulario inicializado.")
        
    return render(request, 'accounts/login.html', {
        'form': form,
        'title': 'Iniciar Sesión'
    })


def signup_view(request):
    logger.info("📝 Vista signup llamada")
    
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        logger.info("📨 POST recibido en signup")
        form = SignupForm(request.POST)
        logger.debug(f"✅ Form signup válido: {form.is_valid()}")
        
        if form.is_valid():
            logger.info("🎯 Formulario de registro válido - creando usuario...")
            user = form.save()
            
            # Opcional: Iniciar sesión automáticamente después del registro
            login(request, user)
            
            messages.success(request, '¡Tu cuenta ha sido creada exitosamente!')
            logger.info("🎉 Registro exitoso. Redirigiendo a índice.")
            return redirect('index')
        else:
            logger.warning("❌ Formulario inválido. Mostrando errores.")
            messages.error(request, 'Ocurrió un error en el registro. Por favor, revisa los datos.')

    else:
        form = SignupForm()
        logger.debug("📥 Petición GET - Formulario inicializado.")
        
    return render(request, 'accounts/signup.html', {
        'form': form,
        'title': 'Registrarse'
    })


@login_required
def logout_view(request):
    logger.info("🚪 Vista logout llamada")
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    logger.info("👋 Sesión cerrada. Redirigiendo a índice.")
    return redirect('index')


@login_required
def profile_view(request):
    logger.info("👤 Vista profile llamada")
    
    # Obtener el historial de pagos (últimos 5)
    try:
        payment_history = PaymentOrder.objects.filter(user=request.user).order_by('-created_at')[:5]
    except Exception:
        payment_history = []
        
    return render(request, 'accounts/profile.html', {
        'payment_history': payment_history,
        'title': 'Mi Perfil'
    })


@login_required
def edit_profile_view(request):
    logger.info("✍️ Vista edit_profile llamada")
    user = request.user
    
    if request.method == 'POST':
        logger.info("📨 POST recibido en edit_profile")
        # El formulario debe recibir los datos POST, los archivos y la instancia del usuario
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        # El is_valid ya no fallará por FileNotFoundError gracias al fix en forms.py
        logger.debug(f"✅ Form editar perfil válido: {form.is_valid()}")
        
        if form.is_valid():
            logger.info("🎯 Form editar perfil válido - guardando...")
            user = form.save(commit=False) # No guardar aún, hay lógica de avatar
            
            # --- Lógica de Avatar ---
            selected_avatar = request.POST.get('selected_avatar', '')
            profile_picture_file = request.FILES.get('profile_picture') # Archivo subido (None si no se subió)

            # 1. Caso A: Se subió una nueva imagen
            if profile_picture_file:
                logger.info("📸 Subida de imagen detectada. Usando archivo nuevo.")
                user.profile_picture = profile_picture_file
                user.selected_avatar = ''  # Limpiar la referencia al avatar del sistema
                
            # 2. Caso B: Se seleccionó un avatar predeterminado
            elif selected_avatar:
                logger.info(f"🔹 Avatar de sistema seleccionado: {selected_avatar}")
                user.selected_avatar = selected_avatar
                user.profile_picture = None  # Limpiar la referencia al archivo subido

            # 3. Caso C: No hay subida de archivo ni cambio de avatar (se mantienen los valores de la instancia)
            else:
                 logger.debug("✨ No se detectó cambio de avatar. Manteniendo estado actual.")
                 pass
            
            # 4. Guardar el usuario y los cambios
            try:
                user.save()
                messages.success(request, '¡Perfil actualizado exitosamente!')
                logger.info("💾 Perfil guardado. Redirigiendo a perfil.")
                return redirect('profile')
            except Exception as e:
                # Capturar cualquier error inesperado al guardar
                messages.error(request, f'Error al guardar el perfil: {str(e)}')
                logger.error(f"❌ Error al guardar en base de datos: {e}")
        
        else:
            logger.warning("❌ Formulario inválido. Mostrando errores.")
            messages.error(request, 'Por favor, corrige los errores del formulario.')
            
    else:
        # Petición GET: Inicializar el formulario con los datos actuales del usuario
        form = CustomUserChangeForm(instance=user)
        logger.debug("📥 Petición GET - Formulario inicializado.")
    
    # Obtener la URL del avatar actual para la vista previa
    current_avatar_url = user.get_profile_picture_url() 
        
    return render(request, 'accounts/edit_profile.html', {
        'form': form, 
        'title': 'Editar Perfil',
        'current_avatar_url': current_avatar_url 
    })


# =========================================================================
# VISTAS DE RECUPERACIÓN DE CONTRASEÑA
# =========================================================================

def forgot_password_view(request):
    logger.info("❓ Vista forgot_password llamada")
    
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email__iexact=email)
            
            # Generar token y tiempo de expiración
            token = generate_secure_token()
            user.password_reset_token = token
            user.password_reset_expires = timezone.now() + timedelta(hours=1)
            user.save(update_fields=['password_reset_token', 'password_reset_expires'])

            # Construir URL de restablecimiento
            reset_url = request.build_absolute_uri(f'/accounts/reset-password/{token}/')
            
            # Enviar correo
            send_mail(
                'Restablecimiento de Contraseña - ChaosCompany',
                f'Hola {user.username},\n\n'
                f'Recibimos una solicitud para restablecer tu contraseña. Haz clic en el siguiente enlace para continuar:\n'
                f'{reset_url}\n\n'
                f'Este enlace expirará en 1 hora. Si no solicitaste esto, ignora este correo.\n\n'
                f'El equipo de ChaosCompany.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            messages.success(request, 'Se ha enviado un correo electrónico con instrucciones para restablecer tu contraseña. Revisa tu bandeja de entrada.')
            logger.info(f"📧 Correo de restablecimiento enviado a {email}")
        
        except CustomUser.DoesNotExist:
            messages.success(request, 'Si la dirección de correo electrónico está registrada, recibirás un enlace de restablecimiento.')
            logger.warning(f"⚠️ Intento de restablecimiento para email no existente: {email}")
        except Exception as e:
            logger.error(f"💥 Error al enviar correo de restablecimiento: {e}")
            messages.error(request, 'Ocurrió un error al procesar tu solicitud. Intenta más tarde.')
        
        return redirect('forgot_password')
        
    return render(request, 'accounts/forgot_password.html', {
        'title': 'Recuperar Contraseña'
    })


def reset_password_view(request, token):
    logger.info(f"🔑 Vista reset_password llamada con token: {token[:10]}...")
    try:
        # Busca el usuario por token y verifica que no haya expirado
        user = CustomUser.objects.get(password_reset_token=token, password_reset_expires__gt=timezone.now())
    except CustomUser.DoesNotExist:
        messages.error(request, 'El enlace de restablecimiento no es válido o ha expirado.')
        return redirect('login')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password and new_password == confirm_password:
            if len(new_password) >= 8:
                user.set_password(new_password)
                user.password_reset_token = None # Invalidar token
                user.password_reset_expires = None
                user.save()
                
                messages.success(request, '¡Tu contraseña ha sido restablecida exitosamente! Ya puedes iniciar sesión.')
                logger.info(f"✅ Contraseña restablecida para usuario: {user.username}")
                return redirect('login')
            else:
                 messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
        else:
            messages.error(request, 'Las contraseñas no coinciden o están vacías.')
            logger.warning("❌ Contraseñas no coinciden en reset.")
            
    return render(request, 'accounts/reset_password.html', {
        'token': token,
        'title': 'Restablecer Contraseña'
    })

# =========================================================================
# VISTAS DE CARRITO Y COMPRA (Implementación Simplificada)
# =========================================================================

# --- Lógica de Carrito ---

@login_required
def cart_view(request):
    logger.info("🛒 Vista cart_view llamada")
    cart_items = request.session.get('cart', [])
    
    # Calcular totales
    total_price = sum(float(item['price']) for item in cart_items)
    tax_amount = total_price * 0.16  # 16% de IVA
    grand_total = total_price + tax_amount
    
    context = {
        'cart_items': cart_items,
        'total_price': round(total_price, 2),
        'tax_amount': round(tax_amount, 2),
        'grand_total': round(grand_total, 2),
    }

    return render(request, 'main/carrito.html', context)


@login_required
def add_to_cart(request):
    logger.info("➕ add_to_cart llamada")
    if request.method == 'POST':
        plan_type = request.POST.get('plan_type')
        price = request.POST.get('price')
        
        if 'cart' not in request.session:
            request.session['cart'] = []
        
        cart_item = {
            'plan_type': plan_type,
            'price': float(price),
            'name': f'Plan {plan_type.title()}'
        }
        
        # Solo permite un ítem de plan a la vez
        request.session['cart'] = [cart_item]
        request.session.modified = True
        
        messages.success(request, f'Plan {plan_type.title()} agregado al carrito.')
    return redirect('cart')


@login_required
def remove_from_cart(request):
    logger.info("➖ remove_from_cart llamada")
    if request.method == 'POST':
        plan_type_to_remove = request.POST.get('plan_type')
        
        if 'cart' in request.session:
            request.session['cart'] = [
                item for item in request.session['cart'] 
                if item.get('plan_type') != plan_type_to_remove
            ]
            request.session.modified = True
            messages.info(request, 'Plan removido del carrito.')
        
    return redirect('cart')


@login_required
def checkout_view(request):
    logger.info("💳 Vista checkout_view llamada - redirigiendo a pago")
    cart_items = request.session.get('cart', [])
    if not cart_items:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('cart')

    # Redirigir directamente al formulario de pago
    return redirect('payment_page')

# --- Lógica de Pago ---

@login_required
def payment_page(request):
    logger.info("💰 Vista payment_page llamada")
    cart_items = request.session.get('cart', [])
    if not cart_items:
        messages.error(request, 'No hay items en el carrito')
        return redirect('cart')
    
    item = cart_items[0]
    plan_type = item.get('plan_type')
    base_price = float(item.get('price', 0))
    
    tax_amount = base_price * 0.16
    total_amount = base_price + tax_amount
    
    return render(request, 'main/payment.html', {
        'plan_type': plan_type,
        'base_price': round(base_price, 2),
        'tax_amount': round(tax_amount, 2),
        'amount': round(total_amount, 2),
        'title': 'Proceso de Pago'
    })

@login_required
def process_payment(request):
    logger.info("⚙️ process_payment llamada")
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario (simulados)
            plan_type = request.POST.get('plan_type')
            amount_str = request.POST.get('amount', '0').replace(',', '.')
            amount = float(amount_str)
            card_number = request.POST.get('card_number', '0000')
            email = request.POST.get('email', request.user.email)

            # SIMULAR PROCESAMIENTO DE PAGO EXITOSO
            transaction_id = str(uuid.uuid4())[:10].upper()
            
            # Crear y completar la orden de pago (el .save() actualizará las fechas)
            order = PaymentOrder.objects.create(
                user=request.user,
                plan_type=plan_type,
                amount=amount,
                status='completed',
                transaction_id=transaction_id,
                payment_method='credit_card', # Hardcodeado para simulación
                card_last_four=card_number[-4:],
                customer_email=email
            )
            
            # Forzar la actualización de la membresía en el modelo CustomUser
            user_profile = request.user
            user_profile.membership_type = plan_type
            user_profile.is_active_member = True
            user_profile.membership_start = timezone.now()
            user_profile.membership_expiry = timezone.now() + timedelta(days=30)
            user_profile.save(update_fields=['membership_type', 'is_active_member', 'membership_start', 'membership_expiry'])

            # Limpiar carrito
            request.session['cart'] = [] 
            
            messages.success(request, f'¡Pago exitoso! Tu suscripción {plan_type.title()} ha sido activada.')
            return redirect('payment_success', order_id=order.id)
            
        except Exception as e:
            logger.error(f"💥 Error procesando el pago: {e}")
            messages.error(request, f'Error procesando el pago: {str(e)}')
            return redirect('payment_page')
    
    return redirect('cart')

@login_required
def payment_success(request, order_id):
    logger.info(f"🎉 Vista payment_success llamada - Orden: {order_id}")
    order = get_object_or_404(PaymentOrder, id=order_id, user=request.user)
    
    return render(request, 'main/payment_success.html', {
        'order': order,
        'title': 'Pago Exitoso'
    })

@login_required
def payment_cancel(request):
    logger.info("❌ Pago cancelado")
    messages.info(request, 'El pago fue cancelado. Puedes intentarlo nuevamente.')
    return redirect('cart')