from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from .models import Usuario, PerfilDermatologico

def tela_cadastro(request):

    # 1. Verifica se o navegador está enviando dados através de um formulário (POST)
    if request.method == "POST":
        # 2. Captura o valor digitado no campo <input name="nome"> do HTML
        nome = request.POST.get('nome')
        # 3. Captura o valor digitado no campo <input name="email"> do HTML
        email = request.POST.get('email')
        # 4. Captura o valor digitado no campo <input name="senha"> do HTML
        senha = request.POST.get('senha') 
        
        # 5. Cria e salva um novo registro na tabela usuario, já com a senha criptografada
        novo_usuario = Usuario.objects.create_user(
            email=email,
            nome_usuario=nome,
            password=senha,
        )

        # 7. Autentica o usuário recém-criado na sessão do navegador (faz o login automático)
        auth_login(request, novo_usuario)
        # 8. Redireciona o usuário logado para a página do questionário (URL name='questionario')
        return redirect('questionario')
        
        # 9. Se a requisição NÃO for POST (ou seja, se for um acesso normal via GET para carregar a página),
        #renderiza e exibe a tela com o formulário de cadastro limpo.
    return render(request, 'core/cadastro.html')


def tela_questionario(request):
    if request.method == "POST":
        # 1. Pega TODAS as respostas do formulário HTML
        idade = request.POST.get('idade')
        tipo_pele = request.POST.get('tipo_pele')
        alergias = request.POST.get('alergias')
        descricao_alergia = request.POST.get('descricaoalergia')
        maquiagem = request.POST.get('maquiagem')
        pontos_sol = int(request.POST.get('reacao_sol', 0))
        base_produto = request.POST.get('base_produto')
        objective = request.POST.get('objetivo')

        porcentagem_calculada = 75  # Valor padrão, calculado sem análise de IA
        usa_maquiagem = 'sim' if maquiagem == '1' else 'nao'

        # 2. Salva ou atualiza as informações no banco de dados
        if request.user.is_authenticated:
            perfil, created = PerfilDermatologico.objects.get_or_create(
                usuario=request.user,
                defaults={
                    'idade': int(idade) if idade else 0,
                    'tipo_pele': tipo_pele or 'normal',
                    'alergias': alergias or '',
                    'objetivo': objective or 'Melhorar a pele',
                    'preferencia_produto': base_produto if base_produto in ('creme', 'gel') else 'gel',
                    'usa_maquiagem_diariamente': usa_maquiagem,
                    'porcentagem_saude': porcentagem_calculada,
                    'fototipo': pontos_sol + 1,
                }
            )

            perfil.idade = int(idade) if idade else perfil.idade
            perfil.tipo_pele = tipo_pele or perfil.tipo_pele
            perfil.alergias = alergias or perfil.alergias
            perfil.usa_maquiagem_diariamente = usa_maquiagem
            perfil.fototipo = pontos_sol + 1
            perfil.objetivo = objective or perfil.objetivo
            perfil.preferencia_produto = base_produto if base_produto in ('creme', 'gel') else perfil.preferencia_produto
            perfil.porcentagem_saude = porcentagem_calculada

            perfil.save()

        return redirect('dashboard')

    return render(request, 'core/questionario.html')


def tela_sucesso(request):
    return render(request, 'core/sucesso.html')


def dashboard_view(request):
    if request.user.is_authenticated:
        perfil = PerfilDermatologico.objects.filter(usuario=request.user).first()
    else:
        perfil = PerfilDermatologico.objects.first()

    rotina_manha = []
    rotina_noite = []
    if perfil:
        rotina_manha = [
            {
                'class': 'completed',
                'title': 'Limpeza Suave',
                'description': f'Rotina de limpeza diária para pele {perfil.tipo_pele}',
                'time': '08:00',
                'action': None,
                'icon': 'fa-check',
            },
            {
                'class': 'action-required' if perfil.porcentagem_saude < 80 else 'completed',
                'title': 'Hidratação & Tratamento',
                'description': f'Sérum recomendado para objetivo "{perfil.objetivo}"',
                'time': None if perfil.porcentagem_saude < 80 else '19:00',
                'action': 'Fazer agora' if perfil.porcentagem_saude < 80 else None,
                'icon': 'fa-check' if perfil.porcentagem_saude >= 80 else None,
            },
            {
                'class': 'pending' if perfil.fototipo and perfil.fototipo < 5 else 'completed',
                'title': 'Proteção Solar',
                'description': f'FPS 50+ para fototipo {perfil.fototipo or "1"}',
                'time': '12:00' if perfil.fototipo and perfil.fototipo < 5 else 'Já feito',
                'action': None,
                'icon': 'fa-check' if perfil.fototipo and perfil.fototipo >= 5 else None,
            },
        ]
        rotina_noite = [
            {
                'class': 'completed',
                'title': 'Remoção de Maquiagem',
                'description': 'Demaquilante suave antes de dormir',
                'time': '21:00',
                'action': None,
                'icon': 'fa-check',
            },
            {
                'class': 'completed',
                'title': 'Tratamento Noturno',
                'description': f'Sérum calmante para {perfil.tipo_pele}',
                'time': '21:30',
                'action': None,
                'icon': 'fa-check',
            },
            {
                'class': 'pending',
                'title': 'Hidratação Profunda',
                'description': 'Creme nutritivo para reparar enquanto dorme',
                'time': '22:00',
                'action': 'Aplicar agora',
                'icon': None,
            },
        ]

    context = {
        'perfil': perfil,
        'rotina_manha': rotina_manha,
        'rotina_noite': rotina_noite,
    }
    return render(request, 'core/dashboard.html', context)


def tela_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        usuario = authenticate(request, username=email, password=senha)
        
        if usuario is not None:
            auth_login(request, usuario)
            return redirect('dashboard')
        else:
            return render(request, 'core/login.html', {'erro': 'Usuário ou senha incorretos'})
            
    return render(request, 'core/login.html')