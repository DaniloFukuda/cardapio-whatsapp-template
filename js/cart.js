/**
 * Gerenciamento do Carrinho
 * Utiliza localStorage para persistir os dados
 */

class Cart {
  constructor() {
    this.storageKey = 'cardapio_cart';
    this.load();
  }

  /**
   * Carrega o carrinho do localStorage
   */
  load() {
    const data = localStorage.getItem(this.storageKey);
    this.items = data ? JSON.parse(data) : [];
  }

  /**
   * Salva o carrinho no localStorage
   */
  save() {
    localStorage.setItem(this.storageKey, JSON.stringify(this.items));
  }

  /**
   * Adiciona um produto ao carrinho
   */
  adicionar(produto, quantidade = 1) {
    const itemExistente = this.items.find(item => item.id === produto.id);
    
    if (itemExistente) {
      itemExistente.quantidade += quantidade;
    } else {
      this.items.push({
        id: produto.id,
        nome: produto.nome,
        preco: produto.preco,
        quantidade: quantidade,
        categoria: produto.categoria,
        imagem: produto.imagem
      });
    }
    
    this.save();
  }

  /**
   * Remove um produto do carrinho
   */
  remover(produtoId) {
    this.items = this.items.filter(item => item.id !== produtoId);
    this.save();
  }

  /**
   * Aumenta a quantidade de um produto
   */
  aumentarQuantidade(produtoId) {
    const item = this.items.find(item => item.id === produtoId);
    if (item) {
      item.quantidade++;
      this.save();
    }
  }

  /**
   * Diminui a quantidade de um produto
   */
  diminuirQuantidade(produtoId) {
    const item = this.items.find(item => item.id === produtoId);
    if (item && item.quantidade > 1) {
      item.quantidade--;
      this.save();
    } else if (item && item.quantidade === 1) {
      this.remover(produtoId);
    }
  }

  /**
   * Retorna o total de itens
   */
  obterQuantidadeTotal() {
    return this.items.reduce((total, item) => total + item.quantidade, 0);
  }

  /**
   * Retorna o valor total
   */
  obterValorTotal() {
    return this.items.reduce((total, item) => total + (item.preco * item.quantidade), 0);
  }

  /**
   * Retorna todos os itens
   */
  obterItems() {
    return this.items;
  }

  /**
   * Limpa o carrinho
   */
  limpar() {
    this.items = [];
    this.save();
  }

  /**
   * Verifica se o carrinho está vazio
   */
  estaVazio() {
    return this.items.length === 0;
  }
}

// Instância global do carrinho
const carrinho = new Cart();
