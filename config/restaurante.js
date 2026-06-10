/**
 * Configuração do Restaurante
 * Edite este arquivo para personalizar o restaurante
 */

const Restaurante = {
  // Informações básicas
  nome: 'Sabor Brasileiro',
  slogan: 'Comida caseira, sabor de família',
  
  // Contato
  whatsapp: '5511999999999', // Número com código do país e DDD, sem formatação
  instagram: '@seu.restaurante',
  
  // Endereço e horários
  endereco: 'Rua das Flores, 123 - São Paulo, SP',
  horario: 'Seg-Dom: 11h às 22h',
  statusAberto: 'Aberto agora',
  tempoEntrega: '35-50 min',
  pedidoMinimo: 15.00,
  
  // Configurações de entrega
  taxaEntregaPadrao: 5.00,
  aceitaEntrega: true,
  aceitaRetirada: true,
  
  // Visuais
  logo: '🍲', // Pode ser URL ou emoji
  bannerImagem: '', // URL de imagem de destaque para a home / cardápio
  bannerTitulo: 'Comida de verdade, feita para o seu dia',
  bannerTexto: 'Escolha seus favoritos e envie o pedido pronto pelo WhatsApp.',
  produtosDestaque: ['feijoada', 'frango-grelhado', 'marmita-media'],
  cores: {
    principal: '#E74C3C',    // Vermelho quente
    secundaria: '#F39C12',   // Laranja
    fundo: '#FFF8F3',        // Bege claro
    texto: '#2C3E50'         // Cinza escuro
  }
};
