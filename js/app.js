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
  App.init();
});
