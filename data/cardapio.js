/**
 * Cardápio do Restaurante
 * Edite este arquivo para adicionar, remover ou alterar produtos
 */

const Cardapio = {
  categorias: [
    {
      id: 'marmitas',
      nome: 'Marmitas',
      descricao: 'Pratos prontos em embalagem térmica',
      produtos: [
        {
          id: 'marmita-pequena',
          nome: 'Marmita Pequena',
          descricao: 'Arroz, feijão, proteína e acompanhamento',
          preco: 15.00,
          imagem: '🍚'
        },
        {
          id: 'marmita-media',
          nome: 'Marmita Média',
          descricao: 'Porção aumentada de proteína e acompanhamento',
          preco: 22.00,
          imagem: '🍚'
        },
        {
          id: 'marmita-grande',
          nome: 'Marmita Grande',
          descricao: 'Grande quantidade de proteína, ideal para 2 pessoas',
          preco: 32.00,
          imagem: '🍚'
        }
      ]
    },
    {
      id: 'pratos-feitos',
      nome: 'Pratos Feitos',
      descricao: 'Nossos pratos mais populares',
      produtos: [
        {
          id: 'prato-feito',
          nome: 'Prato Feito',
          descricao: 'Escolha a proteína: frango, carne ou peixe',
          preco: 18.00,
          imagem: '🍗'
        },
        {
          id: 'feijoada',
          nome: 'Feijoada Completa',
          descricao: 'Feijão preto com carnes, arroz, couve e laranja',
          preco: 28.00,
          imagem: '🍲'
        },
        {
          id: 'frango-grelhado',
          nome: 'Frango Grelhado',
          descricao: 'Peito de frango grelhado com queijo derretido',
          preco: 24.00,
          imagem: '🍗'
        },
        {
          id: 'bife-acebolado',
          nome: 'Bife à Acebolada',
          descricao: 'Bife suculento com molho de cebola caramelizada',
          preco: 26.00,
          imagem: '🥩'
        }
      ]
    },
    {
      id: 'bebidas',
      nome: 'Bebidas',
      descricao: 'Refrigerantes, sucos e água',
      produtos: [
        {
          id: 'refrigerante-lata',
          nome: 'Refrigerante Lata',
          descricao: 'Coca, Guaraná ou Fanta (350ml)',
          preco: 3.50,
          imagem: '🥤'
        },
        {
          id: 'suco-natural',
          nome: 'Suco Natural',
          descricao: 'Laranja ou Melancia (300ml)',
          preco: 5.00,
          imagem: '🧃'
        },
        {
          id: 'agua',
          nome: 'Água',
          descricao: 'Água mineral (500ml)',
          preco: 2.00,
          imagem: '💧'
        }
      ]
    },
    {
      id: 'adicionais',
      nome: 'Adicionais',
      descricao: 'Complementos para seu prato',
      produtos: [
        {
          id: 'ovo-extra',
          nome: 'Ovo Extra',
          descricao: 'Ovo frito ou cozido',
          preco: 3.00,
          imagem: '🥚'
        },
        {
          id: 'farofa',
          nome: 'Farofa',
          descricao: 'Porção de farofa caseira',
          preco: 2.50,
          imagem: '🌾'
        },
        {
          id: 'salada-extra',
          nome: 'Salada Extra',
          descricao: 'Tomate, alface e cebola',
          preco: 4.00,
          imagem: '🥗'
        },
        {
          id: 'feijao-extra',
          nome: 'Feijão Extra',
          descricao: 'Porção extra de feijão',
          preco: 3.00,
          imagem: '🍲'
        }
      ]
    }
  ],

  /**
   * Encontra um produto pelo ID
   */
  obterProduto(id) {
    for (let categoria of this.categorias) {
      const produto = categoria.produtos.find(p => p.id === id);
      if (produto) {
        return { ...produto, categoria: categoria.nome, categoriaId: categoria.id };
      }
    }
    return null;
  },

  /**
   * Retorna todos os produtos de uma categoria
   */
  obterPorCategoria(categoriaId) {
    const categoria = this.categorias.find(c => c.id === categoriaId);
    return categoria ? categoria.produtos : [];
  }
};
