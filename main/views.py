# main/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import uuid
from accounts.models import PaymentOrder

def index(request):
    return render(request, 'main/index.html', {'title': 'Inicio'})

def membresias(request):
    return render(request, 'main/membresias.html', {'title': 'Membresías'})

def gamepass(request):
    juegos_destacados = [
        {
            'nombre': 'Grand Theft Auto V',
            'imagen': 'Imagenes/gtav.webp',
            'descripcion': 'Explora el mundo abierto de Los Santos y vive una vida de crimen y aventuras.',
            'categoria': 'Mundo Abierto'
        },
        {
            'nombre': 'Forza Horizon 5',
            'imagen': 'Imagenes/Forza5.webp',
            'descripcion': 'Conduce por los paisajes increíbles de México en este emocionante juego de carreras.',
            'categoria': 'Carreras'
        },
        {
            'nombre': 'Fortnite',
            'imagen': 'Imagenes/Fortnite.webp',
            'descripcion': 'Únete a la batalla campal y construye tu camino hacia la victoria.',
            'categoria': 'Battle Royale'
        },
    ]
    categorias = {
        'Acción': ['GTA V', 'Call of Duty', 'Battlefield'],
        'Aventura': ['The Legend of Zelda', 'Uncharted', 'Tomb Raider'],
        'Deportes': ['FIFA 24', 'NBA 2K24', 'Rocket League'],
        'Estrategia': ['Age of Empires', 'Civilization VI', 'StarCraft II']
    }
    context = {
        'juegos_destacados': juegos_destacados,
        'categorias': categorias,
        'title': 'Gamepass'
    }
    return render(request, 'main/gamepass.html', context)

def ventajas(request):
    return render(request, 'main/ventajas.html', {'title': 'Ventajas'})

@login_required
def game_session(request):
    game_name = request.GET.get('game', 'Juego Desconocido')
    if request.user.membership_type == 'free':
        messages.warning(request, 'Necesitas una membresía premium para jugar este juego.')
        return render(request, 'main/membresias.html', {'title': 'Membresías'})
    context = {
        'game_name': game_name,
        'title': f'Jugando {game_name}'
    }
    return render(request, 'main/game_session.html', context)

# ===== VISTAS DE PAGO =====
@login_required
def cart(request):
    """Vista del carrito de compras"""
    cart_items = request.session.get('cart', [])
    
    # Calcular totales
    total_price = 0
    for item in cart_items:
        total_price += float(item.get('price', 0))
    
    tax_amount = total_price * 0.16
    grand_total = total_price + tax_amount
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'tax_amount': tax_amount,
        'grand_total': grand_total,
        'title': 'Carrito de Compras'
    }
    return render(request, 'main/carrito.html', context)

@login_required
def add_to_cart(request):
    """Agregar membresía al carrito"""
    if request.method == 'POST':
        plan_type = request.POST.get('plan_type')
        price = float(request.POST.get('price', 0))
        
        # Crear item del carrito
        cart_item = {
            'plan_type': plan_type,
            'price': price,
            'name': f'Plan {plan_type.capitalize()}'
        }
        
        # Inicializar carrito si no existe
        if 'cart' not in request.session:
            request.session['cart'] = []
        
        # Limpiar carrito anterior y agregar nuevo item (solo una membresía a la vez)
        request.session['cart'] = [cart_item]
        request.session.modified = True
        
        messages.success(request, f'Plan {plan_type.capitalize()} agregado al carrito')
        return redirect('cart')
    
    return redirect('membresias')

@login_required
def remove_from_cart(request):
    """Remover item del carrito"""
    if request.method == 'POST':
        if 'cart' in request.session:
            del request.session['cart']
            request.session.modified = True
            messages.info(request, 'Item removido del carrito')
    
    return redirect('cart')

@login_required
def payment_page(request):
    """Página del formulario de pago"""
    # Obtener datos del carrito
    cart_items = request.session.get('cart', [])
    if not cart_items:
        messages.error(request, 'No hay items en el carrito')
        return redirect('cart')
    
    item = cart_items[0]
    plan_type = item.get('plan_type')
    base_price = float(item.get('price', 0))
    
    # Calcular impuestos y total
    tax_amount = base_price * 0.16 if base_price > 0 else 0
    total_amount = base_price + tax_amount
    
    return render(request, 'main/payment.html', {
        'plan_type': plan_type,
        'base_price': base_price,
        'tax_amount': round(tax_amount, 2),
        'amount': round(total_amount, 2),
        'title': 'Proceso de Pago'
    })

@login_required
def process_payment(request):
    """Procesar el pago del usuario"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            plan_type = request.POST.get('plan_type')
            amount = float(request.POST.get('amount', 0))
            card_holder = request.POST.get('card_holder', '').strip()
            card_number = request.POST.get('card_number', '').replace(' ', '')
            expiry_date = request.POST.get('expiry_date')
            cvv = request.POST.get('cvv')
            email = request.POST.get('email', request.user.email)
            
            # Validaciones básicas
            if not all([card_holder, card_number, expiry_date, cvv]):
                messages.error(request, 'Todos los campos son obligatorios')
                return redirect('payment_page')
            
            if len(card_number) < 13:
                messages.error(request, 'Número de tarjeta inválido')
                return redirect('payment_page')
            
            if len(cvv) != 3:
                messages.error(request, 'CVV inválido')
                return redirect('payment_page')
            
            # Validar fecha de expiración
            try:
                month, year = expiry_date.split('/')
                month = int(month)
                year = int('20' + year)  # Asumimos años 2000+
                
                current_date = timezone.now()
                if year < current_date.year or (year == current_date.year and month < current_date.month):
                    messages.error(request, 'La tarjeta ha expirado')
                    return redirect('payment_page')
            except ValueError:
                messages.error(request, 'Formato de fecha inválido (MM/AA)')
                return redirect('payment_page')
            
            # SIMULAR PROCESAMIENTO DE PAGO EXITOSO
            transaction_id = str(uuid.uuid4())[:8].upper()
            
            # Crear orden de compra
            order = PaymentOrder.objects.create(
                user=request.user,
                plan_type=plan_type,
                amount=amount,
                status='completed',
                payment_method='credit_card',
                transaction_id=transaction_id,
                card_last_four=card_number[-4:],
                customer_email=email
            )
            
            # Actualizar membresía del usuario
            request.user.membership_type = plan_type
            request.user.membership_start = timezone.now()
            request.user.membership_expiry = timezone.now() + timezone.timedelta(days=30)
            request.user.is_active_member = True
            request.user.save()
            
            # Limpiar carrito
            if 'cart' in request.session:
                del request.session['cart']
            
            messages.success(request, f'¡Pago exitoso! Tu suscripción {plan_type} ha sido activada.')
            return redirect('payment_success', order_id=order.id)
            
        except Exception as e:
            messages.error(request, f'Error procesando el pago: {str(e)}')
            return redirect('payment_page')
    
    return redirect('cart')

@login_required
def payment_success(request, order_id):
    """Página de confirmación de pago exitoso"""
    order = get_object_or_404(PaymentOrder, id=order_id, user=request.user)
    return render(request, 'main/payment_success.html', {
        'order': order,
        'title': 'Pago Exitoso'
    })

@login_required
def payment_cancel(request):
    """Página para pagos cancelados"""
    messages.info(request, 'El pago fue cancelado. Puedes intentarlo nuevamente.')
    return redirect('cart')