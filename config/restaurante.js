/**
 * Configuração do Restaurante
 * Edite este arquivo para personalizar o restaurante
 */

const Restaurante = {
  // Informações básicas
  nome: 'Sabor Brasileiro',
  slogan: 'Comida caseira, sabor de família',
  
  // Contato
  whatsapp: '5511987654321', // Número com código do país e DDD, sem formatação
  instagram: '@sabor.brasileiro',
  
  // Endereço e horários
  endereco: 'Rua das Flores, 123 - São Paulo, SP',
  horario: 'Seg-Dom: 11h às 22h',
  
  // Configurações de entrega
  taxaEntregaPadrao: 5.00,
  aceitaEntrega: true,
  aceitaRetirada: true,
  
  // Visuais
  logo: '🍲', // Pode ser URL ou emoji
  cores: {
    principal: '#E74C3C',    // Vermelho quente
    secundaria: '#F39C12',   // Laranja
    fundo: '#FFF8F3',        // Bege claro
    texto: '#2C3E50'         // Cinza escuro
  }
};
