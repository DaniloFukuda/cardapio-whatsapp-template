class CardapioService {
  constructor(url = 'data/cardapio.json') {
    this.url = url;
    this.dados = null;
  }

  async carregar() {
    const resposta = await fetch(this.url, { cache: 'no-store' });
    if (!resposta.ok) {
      throw new Error('Não foi possível carregar o cardápio do dia.');
    }

    const dados = await resposta.json();
    this.dados = this.normalizar(dados);
    return this.dados;
  }

  normalizar(dados) {
    const tiposMarmita = Array.isArray(dados.tipos_marmita) ? dados.tipos_marmita : [];
    const carnes = Array.isArray(dados.carnes_do_dia) ? dados.carnes_do_dia : [];
    const churrasco = carnes.find(carne => carne.id === 'churrasco');

    if (!churrasco) {
      carnes.unshift({ id: 'churrasco', nome: 'Churrasco', fixo: true });
    } else {
      churrasco.fixo = true;
    }

    return {
      tipos_marmita: tiposMarmita,
      carnes_do_dia: carnes
    };
  }

  listarTiposMarmita() {
    return this.dados?.tipos_marmita.map(tipo => ({ ...tipo })) || [];
  }

  listarCarnesDoDia() {
    return this.dados?.carnes_do_dia.map(carne => ({ ...carne })) || [];
  }

  obterTipoMarmita(id) {
    return this.dados?.tipos_marmita.find(tipo => tipo.id === id) || null;
  }

  obterCarne(id) {
    return this.dados?.carnes_do_dia.find(carne => carne.id === id) || null;
  }

  interpretarEscolhaCarnes(resposta) {
    const carnes = this.listarCarnesDoDia();
    const indices = String(resposta)
      .trim()
      .split(/(?:\s*e\s*|[\s,;]+)/i)
      .filter(Boolean)
      .map(valor => Number.parseInt(valor, 10));

    if (indices.some(indice => !Number.isInteger(indice) || indice < 1 || indice > carnes.length)) {
      return [];
    }

    return [...new Set(indices)].map(indice => carnes[indice - 1].id);
  }

  validarEscolhaCarne(carneId) {
    return Boolean(this.obterCarne(carneId));
  }

  validarQuantidadeCarnes(tipoMarmitaId, carnesIds) {
    const tipo = this.obterTipoMarmita(tipoMarmitaId);
    const idsUnicos = [...new Set(carnesIds || [])];

    if (!tipo || idsUnicos.some(id => !this.validarEscolhaCarne(id))) {
      return {
        valido: false,
        erro: 'Escolha uma opção de carne disponível no cardápio de hoje.'
      };
    }

    if (idsUnicos.length !== tipo.quantidade_carnes) {
      const quantidade = tipo.quantidade_carnes;
      return {
        valido: false,
        erro: `Escolha exatamente ${quantidade} ${quantidade === 1 ? 'carne' : 'carnes'}.`
      };
    }

    return { valido: true };
  }

  criarItemPedido(tipoMarmitaId, carnesIds, quantidade) {
    const tipo = this.obterTipoMarmita(tipoMarmitaId);
    const validacao = this.validarQuantidadeCarnes(tipoMarmitaId, carnesIds);
    const quantidadeNormalizada = Number.parseInt(quantidade, 10);

    if (!validacao.valido) {
      throw new Error(validacao.erro);
    }

    if (!Number.isInteger(quantidadeNormalizada) || quantidadeNormalizada < 1) {
      throw new Error('Informe uma quantidade válida.');
    }

    const carnes = carnesIds.map(id => this.obterCarne(id));
    const variante = [...carnesIds].sort().join('-');

    return {
      id: `${tipo.id}--${variante}`,
      tipoMarmitaId: tipo.id,
      nome: tipo.nome,
      descricao: tipo.descricao,
      preco: tipo.preco,
      quantidade: quantidadeNormalizada,
      quantidadeCarnes: tipo.quantidade_carnes,
      carnes: carnes.map(carne => ({ id: carne.id, nome: carne.nome })),
      imagem: '🍱'
    };
  }

  formatarItemPedido(item) {
    const nomesCarnes = item.carnes.map(carne => carne.nome).join(' e ');
    const total = item.preco * item.quantidade;

    return [
      `${item.quantidade}x ${item.nome}`,
      `Carnes: ${nomesCarnes}`,
      `Valor unitário: ${this.formatarMoeda(item.preco)}`,
      `Total: ${this.formatarMoeda(total)}`
    ].join('\n');
  }

  formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor);
  }
}

const cardapioService = new CardapioService();
