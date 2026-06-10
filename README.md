# Cardápio WhatsApp Template

Template genérico de cardápio digital com visual mobile de app de delivery. O cliente escolhe os produtos, monta o pedido e envia uma mensagem pronta para o WhatsApp do restaurante.

## Recursos

- HTML, CSS e JavaScript puro
- Sem backend e sem bibliotecas externas
- Interface mobile-first inspirada em aplicativos de delivery
- Cabeçalho com logo, status, horário e contato
- Banner personalizável
- Categorias em navegação horizontal sticky
- Produtos com imagem ou placeholder, descrição, preço e botão de adição
- Seção configurável de produtos mais pedidos
- Carrinho persistido em `localStorage`
- Barra inferior do carrinho com quantidade e total
- Checkout com entrega/retirada, pagamento e observações
- Geração do link `wa.me` com o pedido formatado

## Executar localmente

Na pasta do projeto:

```bash
python -m http.server 8000
```

Acesse `http://localhost:8000`.

## Personalizar o restaurante

Edite [`config/restaurante.js`](config/restaurante.js):

```javascript
const Restaurante = {
  nome: 'Seu Restaurante',
  slogan: 'Seu slogan',
  whatsapp: '5511999999999',
  instagram: '@seu.restaurante',
  endereco: 'Rua Exemplo, 123',
  horario: 'Seg-Dom: 11h às 22h',
  statusAberto: 'Aberto agora',
  tempoEntrega: '35-50 min',
  pedidoMinimo: 15.00,

  taxaEntregaPadrao: 5.00,
  aceitaEntrega: true,
  aceitaRetirada: true,

  logo: '🍲',
  bannerImagem: '',
  bannerTitulo: 'Comida de verdade, feita para o seu dia',
  bannerTexto: 'Escolha seus favoritos e envie o pedido pelo WhatsApp.',
  produtosDestaque: ['produto-1', 'produto-2'],

  cores: {
    principal: '#E74C3C',
    secundaria: '#F39C12',
    fundo: '#FFF8F3',
    texto: '#2C3E50'
  }
};
```

`logo`, `bannerImagem` e a propriedade `imagem` dos produtos aceitam URL, caminho local como `assets/foto.jpg` ou emoji. Se uma imagem não carregar, o template exibe um placeholder.

## Personalizar o cardápio

Edite [`data/cardapio.js`](data/cardapio.js):

```javascript
{
  id: 'produto-1',
  nome: 'Nome do produto',
  descricao: 'Descrição curta do produto',
  preco: 25.00,
  imagem: 'assets/produto.jpg'
}
```

Cada produto deve ter um `id` único. Use esses IDs em `produtosDestaque` para escolher os itens da seção “Mais pedidos”. Quando a lista não é configurada, o template usa os primeiros produtos do cardápio.

## Fluxo do pedido

1. `index.html`: apresentação e informações do restaurante.
2. `cardapio.html`: categorias, produtos, destaques e carrinho.
3. `pedido.html`: conferência, modalidade, pagamento e observações.
4. WhatsApp: abertura do `wa.me` com a mensagem formatada.

O carrinho fica salvo no navegador com `localStorage` e é limpo depois do envio do pedido.

## Estrutura

```text
cardapio-whatsapp-template/
├── index.html
├── cardapio.html
├── pedido.html
├── config/
│   └── restaurante.js
├── data/
│   └── cardapio.js
├── css/
│   └── style.css
├── js/
│   ├── app.js
│   ├── cart.js
│   └── whatsapp.js
└── assets/
```

## Publicação

Por ser um projeto estático, pode ser publicado no GitHub Pages, Netlify, Vercel ou qualquer hospedagem de arquivos HTML.

O WhatsApp deve estar no formato internacional, somente com números. Exemplo: `5511987654321`.
