/**
 * Integração com WhatsApp
 * Formata e envia mensagens para o número configurado
 */

class WhatsAppIntegration {
  /**
   * Formata a mensagem do pedido
   */
  static gerarMensagem(dados) {
    const {
      nomeCliente,
      telefoneCliente,
      items,
      tipoPedido, // 'entrega' ou 'retirada'
      endereco,
      pagamento,
      troco,
      observacoes,
      taxa,
      total
    } = dados;

    let mensagem = `*${Restaurante.nome}*\n`;
    mensagem += `===================\n\n`;

    // Dados do cliente
    mensagem += `*Dados do Cliente:*\n`;
    mensagem += `👤 ${nomeCliente}\n`;
    if (telefoneCliente) {
      mensagem += `📱 ${telefoneCliente}\n`;
    }
    mensagem += `\n`;

    // Tipo de pedido
    mensagem += `*Tipo de Pedido:*\n`;
    if (tipoPedido === 'entrega') {
      mensagem += `🚚 Entrega\n`;
      if (endereco) {
        mensagem += `📍 ${endereco}\n`;
      }
    } else {
      mensagem += `🏪 Retirada\n`;
    }
    mensagem += `\n`;

    // Itens do pedido
    mensagem += `*Seu Pedido:*\n`;
    let subtotal = 0;
    items.forEach(item => {
      const valorItem = item.preco * item.quantidade;
      subtotal += valorItem;
      mensagem += `• ${item.quantidade}x ${item.nome} - R$ ${valorItem.toFixed(2)}\n`;
    });
    mensagem += `\n`;

    // Resumo financeiro
    mensagem += `*Resumo do Pedido:*\n`;
    mensagem += `Subtotal: R$ ${subtotal.toFixed(2)}\n`;
    
    if (tipoPedido === 'entrega' && taxa > 0) {
      mensagem += `Taxa de entrega: R$ ${taxa.toFixed(2)}\n`;
    }
    
    mensagem += `*Total: R$ ${total.toFixed(2)}*\n\n`;

    // Forma de pagamento
    mensagem += `*Pagamento:*\n`;
    if (pagamento === 'pix') {
      mensagem += `Pix\n`;
    } else if (pagamento === 'dinheiro') {
      mensagem += `Dinheiro\n`;
      if (troco) {
        mensagem += `Troco para: R$ ${troco.toFixed(2)}\n`;
      }
    } else if (pagamento === 'cartao') {
      mensagem += `Cartão de crédito/débito\n`;
    }
    mensagem += `\n`;

    // Observações
    if (observacoes) {
      mensagem += `*Observações:*\n`;
      mensagem += `${observacoes}\n`;
    }

    return mensagem;
  }

  /**
   * Abre o WhatsApp com a mensagem formatada
   */
  static enviarPedido(dados) {
    const mensagem = this.gerarMensagem(dados);
    const numeroWhatsApp = Restaurante.whatsapp;
    
    // Codifica a mensagem para URL
    const mensagemCodificada = encodeURIComponent(mensagem);
    
    // Monta a URL do wa.me
    const url = `https://wa.me/${numeroWhatsApp}?text=${mensagemCodificada}`;
    
    // Abre em nova aba
    window.open(url, '_blank');
  }

  /**
   * Valida dados necessários
   */
  static validarDados(dados) {
    if (!dados.nomeCliente || dados.nomeCliente.trim() === '') {
      return { valido: false, erro: 'Nome do cliente é obrigatório' };
    }

    if (!dados.items || dados.items.length === 0) {
      return { valido: false, erro: 'Carrinho está vazio' };
    }

    if (dados.tipoPedido === 'entrega' && (!dados.endereco || dados.endereco.trim() === '')) {
      return { valido: false, erro: 'Endereço é obrigatório para entrega' };
    }

    if (!dados.pagamento) {
      return { valido: false, erro: 'Escolha uma forma de pagamento' };
    }

    if (dados.pagamento === 'dinheiro' && dados.troco && dados.troco < dados.total) {
      return { valido: false, erro: 'Troco insuficiente' };
    }

    return { valido: true };
  }
}
