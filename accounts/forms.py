from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import CustomUser

# =========================================================================
# FORMULARIO DE INICIO DE SESIÓN
# =========================================================================

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input-field', 
            'placeholder': 'Usuario o correo electrónico',
            'required': 'true',
            'autocomplete': 'off'
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input-field', 
            'placeholder': 'Contraseña',
            'required': 'true'
        })
    )
    remember_me = forms.BooleanField(
        required=False
    )
    
    # Personalización del mensaje de error
    error_messages = {
        'invalid_login': "Por favor, introduce un nombre de usuario y contraseña correctos. Nota que ambos campos pueden ser sensibles a mayúsculas y minúsculas.",
        'inactive': "Esta cuenta está inactiva.",
    }

# =========================================================================
# FORMULARIO DE REGISTRO
# =========================================================================

class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input-field', 
            'placeholder': 'Correo electrónico',
            'required': 'true'
        })
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input-field', 
            'placeholder': 'Nombre',
            'required': 'true'
        })
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input-field', 
            'placeholder': 'Apellido',
            'required': 'true'
        })
    )
    
    # Campo membership_type con las opciones correctas del modelo
    membership_type = forms.ChoiceField(
        required=True,
        choices=CustomUser._meta.get_field('membership_type').choices,
        widget=forms.Select(attrs={
            'class': 'form-input-field',
            'required': 'true'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'membership_type')
        field_classes = {'username': forms.CharField}
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar campos de contraseña
        self.fields['password_1'].widget.attrs.update({
            'class': 'form-input-field', 
            'placeholder': 'Contraseña',
            'required': 'true'
        })
        self.fields['password_2'].widget.attrs.update({
            'class': 'form-input-field', 
            'placeholder': 'Confirmar contraseña',
            'required': 'true'
        })
        
        # Remover textos de ayuda
        self.fields['password_1'].help_text = ''
        self.fields['password_2'].help_text = ''
        if 'username' in self.fields:
            self.fields['username'].help_text = ''

    # VALIDACIÓN PARA USUARIO EXISTENTE
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise ValidationError('Este nombre de usuario ya está registrado. Por favor elige otro.')
        return username

    # VALIDACIÓN PARA CORREO EXISTENTE
    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise ValidationError('Este correo electrónico ya está registrado. ¿Ya tienes una cuenta?')
        return email

    # VALIDACIÓN PARA CONTRASEÑAS
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Las contraseñas no coinciden. Por favor verifica.')
        
        if len(password1) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
        
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

# =========================================================================
# FORMULARIO DE EDICIÓN DE PERFIL
# =========================================================================

class CustomUserChangeForm(UserChangeForm):
    # Eliminar el campo de contraseña del formulario de edición
    password = None
    
    # Campo para subir imagen personalizada
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'custom-file-input', 'accept': 'image/*'})
    )
    
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-input-field', 'type': 'date'})
    )
    
    class Meta:
        model = CustomUser
        # Incluye todos los campos que quieres que sean editables en el formulario
        fields = ('username', 'email', 'first_name', 'last_name', 'membership_type', 'profile_picture', 'birth_date')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eliminar el campo 'password' que hereda de UserChangeForm para edición de perfil
        if 'password' in self.fields:
            del self.fields['password']
            
        # Añadir clases CSS y placeholders a los campos
        self.fields['username'].widget.attrs.update({
            'class': 'form-input-field',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-input-field',
            'placeholder': 'Correo electrónico'
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-input-field',
            'placeholder': 'Nombre'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-input-field',
            'placeholder': 'Apellido'
        })
        self.fields['membership_type'].widget.attrs.update({
            'class': 'form-input-field'
        })
        self.fields['birth_date'].widget.attrs.update({
            'class': 'form-input-field'
        })
        
        # Personalizar las opciones del membership_type
        self.fields['membership_type'].choices = CustomUser._meta.get_field('membership_type').choices

    # VALIDACIÓN PARA CORREO EXISTENTE (excluyendo el usuario actual)
    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if CustomUser.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Este correo electrónico ya está registrado por otro usuario.')
        return email
    
    # VALIDACIÓN PARA USUARIO EXISTENTE (excluyendo el usuario actual)
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username__iexact=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Este nombre de usuario ya está registrado. Por favor elige otro.')
        return username
    
    # =======================================================================================
    # V A L I D A C I Ó N   C O R R E G I D A   P A R A   L A   I M A G E N   D E   P E R F I L
    # =======================================================================================
    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        
        if profile_picture:
            try:
                # Validar tamaño del archivo (máximo 5MB)
                # FIX: try/except para capturar FileNotFoundError (tu error original)
                if profile_picture.size > 5 * 1024 * 1024:
                    raise ValidationError('La imagen debe ser menor a 5MB.')
            
            except FileNotFoundError:
                # Si el archivo referenciado en el modelo no existe, 
                # permitimos que el formulario sea válido. La vista se encargará
                # de limpiar o reemplazar la referencia.
                pass
                
            # Validar tipo de archivo
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
            
            if hasattr(profile_picture, 'name'):
                extension = profile_picture.name.split('.')[-1].lower()
                if extension not in valid_extensions:
                    raise ValidationError('Formato de imagen no válido. Use JPG, PNG, GIF o WebP.')

        return profile_picture

# =========================================================================
# CLASE REQUERIDA PARA EL ADMIN DE DJANGO
# =========================================================================

# Esta clase es necesaria para evitar el ImportError en accounts/admin.py
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'membership_type')
        # Se necesita `password1` y `password2` para la creación, pero UserCreationForm los añade automáticamente.