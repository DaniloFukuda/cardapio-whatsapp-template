/**
 * Aplicação Principal
 * Funções gerais de navegação e manipulação do DOM
 */

class App {
  static init() {
    // Navega para página inicial se nenhuma página está carregada
    if (document.body.dataset.page === 'index' || !document.body.dataset.page) {
      this.atualizarContador();
    }
  }

  /**
   * Atualiza o contador do carrinho
   */
  static atualizarContador() {
    const contador = document.getElementById('carrinho-contador');
    if (contador) {
      const quantidade = carrinho.obterQuantidadeTotal();
      contador.textContent = quantidade;
      contador.style.display = quantidade > 0 ? 'block' : 'none';
    }
  }

  /**
   * Formata valor em moeda brasileira
   */
  static formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor);
  }

  /**
   * Aplica as cores configuradas no documento.
   */
  static aplicarTema() {
    const root = document.documentElement;
    const cores = Restaurante.cores || {};

    root.style.setProperty('--cor-principal', cores.principal || '#E74C3C');
    root.style.setProperty('--cor-secundaria', cores.secundaria || '#F39C12');
    root.style.setProperty('--cor-fundo', cores.fundo || '#FFF8F3');
    root.style.setProperty('--cor-texto', cores.texto || '#2C3E50');
  }

  /**
   * Renderiza uma URL de imagem ou um emoji dentro de um container.
   */
  static renderizarMidia(container, valor, alt = '') {
    if (!container) return;

    container.replaceChildren();
    if (typeof valor === 'string' && /^(https?:\/\/|\.{0,2}\/|assets\/)/i.test(valor)) {
      const imagem = document.createElement('img');
      imagem.src = valor;
      imagem.alt = alt;
      imagem.loading = 'lazy';
      imagem.addEventListener('error', () => {
        container.replaceChildren(document.createTextNode('🍽️'));
        container.classList.add('midia-placeholder');
      }, { once: true });
      container.appendChild(imagem);
      return;
    }

    container.textContent = valor || '🍽️';
    container.classList.add('midia-placeholder');
  }

  /**
   * Preenche o cabeçalho compartilhado quando os elementos existirem.
   */
  static preencherCabecalho() {
    const campos = {
      'header-restaurante': Restaurante.nome,
      'restaurante-nome': Restaurante.nome,
      'header-slogan': Restaurante.slogan,
      'restaurante-slogan': Restaurante.slogan,
      'header-horario': Restaurante.horario,
      'restaurante-horario': Restaurante.horario,
      'status-aberto': Restaurante.statusAberto || 'Aberto agora'
    };

    Object.entries(campos).forEach(([id, valor]) => {
      const elemento = document.getElementById(id);
      if (elemento && valor) elemento.textContent = valor;
    });

    const logo = document.getElementById('header-logo');
    if (logo) this.renderizarMidia(logo, Restaurante.logo, `Logo ${Restaurante.nome}`);

    document.querySelectorAll('[data-whatsapp]').forEach(link => {
      link.href = `https://wa.me/${Restaurante.whatsapp}`;
    });
  }

  /**
   * Limpa campos de formulário
   */
  static limparFormulario(formId) {
    const form = document.getElementById(formId);
    if (form) {
      form.reset();
    }
  }

  /**
   * Exibe mensagem de feedback
   */
  static mostrarMensagem(texto, tipo = 'sucesso') {
    // Cria elemento de mensagem
    const div = document.createElement('div');
    div.className = `mensagem mensagem-${tipo}`;
    div.textContent = texto;
    
    // Insere no início do body
    document.body.insertBefore(div, document.body.firstChild);
    
    // Remove após 3 segundos
    setTimeout(() => {
      div.remove();
    }, 3000);
  }

  /**
   * Redireciona para outra página
   */
  static irPara(pagina) {
    window.location.href = pagina;
  }
}

// Inicializa a aplicação quando o DOM está pronto
document.addEventListener('DOMContentLoaded', () => {
  App.aplicarTema();
  App.preencherCabecalho();
  App.init();
});
